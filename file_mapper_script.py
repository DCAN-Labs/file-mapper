#! /usr/bin/env python
#
# Requires Python 3
# BASIC USAGE:
#   ./file_mapper_script.py <JSON-file>
#

#import the different python libraries
import os, sys
import json
import argparse
import shutil
import pprint

#non built-in libraries
import boto3


#gives a description over the purpose of the program
PROG = 'File Mapper'
VERSION = '1.3.0'

program_desc = """%(prog)s v%(ver)s:
Script that manuipulates JSON files to create new directories with three
options of copy move and symbolic link.
#""" % {'prog': PROG, 'ver': VERSION}


def get_parser():
    #sets a variable equal to the argparse function which lets a user input
    #choices
    parser = argparse.ArgumentParser(description=program_desc, prog=PROG)

    #gives the absolute path to the json file
    parser.add_argument('jsonpath', nargs=1,
                    help="""Absolute path to a JSON.""")

    #gives the choices as an argument that the user can pass through
    #to manipulate the path of the json file
    parser.add_argument('-a', '--action', dest='action', required=False, default='copy',
                        choices = ['copy', 'move', 'symlink', 'move+symlink'],
                        help="""The different actions of the script which
                        act on the source and destination, with a default of copy.""")
    parser.add_argument('--s3_access_key',required=False,type=str,
                        help='Your S3 access key, if data is within S3. If using MSI, this can be found at: https://www.msi.umn.edu/content/s3-credentials')
    parser.add_argument('--s3_hostname',required=False,default='https://s3.msi.umn.edu',type=str,
                        help='URL for S3 storage hostname, if data is within S3 bucket. Defaults to s3.msi.umn.edu for MSIs tier 2 CEPH storage.')
    parser.add_argument('--s3_secret_key',required=False,type=str,
                        help='Your S3 secret key. If using MSI, this can be found at: https://www.msi.umn.edu/content/s3-credentials')    
    parser.add_argument('-o', '--overwrite', dest='overwrite', required=False,
                        default=False, action = 'store_true',
                        help="""This allows new directories to be created
                        regardless of whether or not they already exist.""")

    parser.add_argument('-s', '--skip-errors', dest='skip_errors',
                        required=False, default=False, action= 'store_true',
                        help="""This skips over the errors in a JSON file so
                        that the other keys/values can be properly read.""")

    parser.add_argument('-sp', '--sourcepath', nargs=1, default=None,
                        required=False, help="""Provides the absolute path to
                        the source of the file being copied/moved/symlinked.""")

    parser.add_argument('-dp', '--destpath', nargs=1, default=None,
                        required=False, help="""Provides the absolute path to
                        the destination of the file being
                        copied/moved/symlinked""")

    parser.add_argument('-t', '--template', nargs=1, default=None,
                        required=False, help="""A no-spaces-allowed, comma-separated
                        list of template fill-ins to replace fields in your JSON of
                        the format: 'TEMPLATE1=REPLACEMENT1,TEMPLATE2=REPLACEMENT2,...'.
                        For example let's say you want to replace a {SUBJECT} and
                        {SESSION} template variable you would use: 
                        -t 'SUBJECT=sub-01,SESSION=ses-baseline'""")

    parser.add_argument('-td', '--testdebug', dest='testdebug', required=False,
                        default=False, action='store_true', help="""Allows user
                        to see what happens when a certain mode is called""")

    parser.add_argument('-vb', '--verbose', dest='verbose', required=False,
                        default=False, action='store_true', help="""Shows all of
                        the print messages when verbose is called""")

    parser.add_argument('-relsym', '--relative-symlink', dest='relative_symlink',
                        required=False, default=False, action='store_true',
                        help="""Allows user to chose whether or not the symlink
                        being created is a relative path so that root
                        directories can be moved without the link breaking.""")

    return parser

# if pulling from s3 will retreive BIDS subjects from bucket
def s3_get_bids_subjects(access_key,bucketName,host,prefix,secret_key):
    client = s3_client(access_key=access_key,host=host,secret_key=secret_key)
    paginator = client.get_paginator('list_objects_v2')
    page_iterator = paginator.paginate(Bucket=bucketName,Delimiter='/',Prefix=prefix,EncodingType='url',ContinuationToken='',
                                             FetchOwner=False,
                                             StartAfter='')
    get_data = client.list_objects_v2(Bucket=bucketName,Delimiter='/',EncodingType='url',
                                            Prefix=prefix,
                                             MaxKeys=1000,
                                             ContinuationToken='',
                                             FetchOwner=False,
                                             StartAfter='')
    bids_subjects = []
    for page in page_iterator:
        page_bids_subjects = ['sub-'+item['Prefix'].split('sub-')[1].strip('/') for item in page['CommonPrefixes'] if 'sub' in item['Prefix']]
        bids_subjects.extend(page_bids_subjects)
    return bids_subjects

# if pull from s3 will retreive BIDS sessions from bucket
def s3_get_bids_sessions(access_key,bucketName,host,prefix,secret_key):
    client = s3_client(access_key=access_key,host=host,secret_key=secret_key)
    get_data = client.list_objects_v2(Bucket=bucketName,Delimiter='/',EncodingType='url',
                                          MaxKeys=1000,
                                          Prefix=prefix,
                                          ContinuationToken='',
                                          FetchOwner=False,
                                          StartAfter='')
    bids_sessions = [item['Prefix'].split('/')[1] for item in get_data['CommonPrefixes'] if 'ses' in item['Prefix'].split('/')[1]]
    return bids_sessions

# download data from s3 bucket using S3
def downloadDirectoryFroms3(bucketName,remoteDirectoryName,access_key,secret_key,host):
    s3_resource = boto3.resource('s3',endpoint_url=host,
                                 aws_access_key_id=access_key, 
                                 aws_secret_access_key=secret_key)
    bucket = s3_resource.Bucket(bucketName) 
    try:
        for object in bucket.objects.filter(Prefix = remoteDirectoryName):
            if not os.path.exists(os.path.dirname(os.path.join(hcp_output_data,object.key))):
                os.makedirs(os.path.dirname(os.path.join(hcp_output_data,object.key)))
                bucket.download_file(object.key,os.path.join(hcp_output_data,object.key))
            else:
                remote_file_size = object.size
                local_file_size = os.stat(os.path.join(hcp_output_data,object.key)).st_size
                if not local_file_size == remote_file_size:
                    bucket.download_file(object.key,os.path.join(hcp_output_data,object.key))


#big function that parses the entire JSON file
def parse_data(data, verbose=False, testdebug=False):
    non_specials_list = []
    #Checks for source and destination arguments in the JSON
    for element in data.keys():
        if element not in ['SOURCE', 'DESTINATION']:
            non_specials_list.append(element)

    if args.template != None:
        template_dict = parse_template(args.template[0])

    for key in non_specials_list:
        #If sourcepath exists the append it to the destination value and overwrite
        if args.sourcepath != None:
            if verbose:
                print("A sourcepath argument exists")
            source = os.path.join(args.sourcepath[0], key)
            if 'SOURCE' in data:
                if verbose:
                    print('Optional SOURCE argument: '+ args.sourcepath[0] +
                    ' overrules source: ' + str(data['SOURCE']))
        elif 'SOURCE' in data:
            if verbose:
                print("Source already exists in json data")
            source = os.path.join(data['SOURCE'],key)
        #If the destination path argument exists then append to the key and overwrites the pre-existing argument
        if args.destpath != None:
            if verbose:
                print("A destination path argument exists")
            destination = os.path.join(args.destpath[0], data[key])
            if 'DESTINATION' in data:
                if verbose:
                    print('Optional DESTINATION argument: '+ args.destpath[0] +
                    ' overrules destination: ' + str(data['DESTINATION']))
        #If the destination argument exists then append it to the key's value
        elif "DESTINATION" in data:
            if verbose:
                print("Destination already exists in json data")
            destination = os.path.join(data['DESTINATION'], data[key])
        else:
            #If neither exists then use pre-existing values
            if verbose:
                print("DESTINATION not provided, using pre-existing values in JSON")
            destination = data[key]

        #Replace any template values in the case of an input template argument
        if args.template != None:
            if '{' in source and '}' in source:
                for lookup in template_dict:
                    source = source.replace('{' + lookup + '}', template_dict[lookup])
            if '{' in destination and '}' in destination:
                for lookup in template_dict:
                    destination = destination.replace('{' + lookup + '}', template_dict[lookup])
        
        #check if the path in the json data actually exists
        if os.path.exists(source) and os.path.isfile(source):
            dirname = os.path.dirname(destination)
            # make a directory based on the key in the json file
            if os.path.isfile(destination):
                if not args.overwrite:
                    if verbose or testdebug:
                        print("Destination file already exists: " + str(destination))
                elif args.overwrite:
                    do_action(source, destination, args.action,
                    overwrite=args.overwrite, testdebug=args.testdebug, relsym=args.relative_symlink)
                    if verbose:
                        print("File has been overwritten")
                elif os.path.exists(dirname):
                    if verbose:
                        print("Path already exists: " + str(dirname))
            elif os.path.isdir(os.path.dirname(destination)):
                do_action(source, destination, args.action, testdebug=args.testdebug, relsym=args.relative_symlink)
            else:
                os.makedirs( dirname )
                if verbose:
                    print("Path has been made: " + str(dirname))
                do_action(source, destination, args.action, testdebug=args.testdebug, relsym=args.relative_symlink)




#Decides what to do based on the action chosen by the user
def do_action(src, dest, action, overwrite=False, testdebug=False, relsym=False):
    if relsym:
        common = os.path.commonpath([os.path.abspath(p) for p in [src,dest]])
        src_from_common = os.path.relpath(src,common)
        dest_from_common = os.path.relpath(dest,common)
        rel_src_from_dest = os.sep.join(['..' for _ in dest_from_common.split(os.sep)[:-1]] + [src_from_common])
        rel_dest_from_src = os.sep.join(['..' for _ in src_from_common.split(os.sep)[:-1]] + [dest_from_common])
        
    if overwrite:
        overwrite_string = 'overwrite '
    else:
        overwrite_string = ''
        #If testdebug mode is present then a string will be constructed based on the arguments provided by the user
        if testdebug:
            print(overwrite_string + action + ': ' + src + ' -> ' + str(dest))
        else:
            #copies the file from one directory to another
            if action == "copy":
                if overwrite:
                    os.remove(dest)
                shutil.copy(src, dest)
            #moves the file from one directory to another
            elif action == "move":
                if overwrite:
                    os.remove(dest)
                shutil.move(src, dest)
            #symlinks the file from one directory to another
            elif action == "symlink":
                if overwrite:
                    os.unlink(dest)
                if relsym:
                    os.symlink(rel_src_from_dest, dest)
                else:
                    os.symlink(src, dest)
            #moves the file from one directory to another AND symlinks it back to its source
            elif action == "move+symlink":
                if overwrite:
                    os.remove(dest)
                shutil.move(src, dest)
                if relsym:
                    os.symlink(rel_dest_from_src, src)
                else:
                    os.symlink(dest, src)
            elif action=="s3cmd":
                if overwrite:
                    os.remove(dest)
                cmd="s3cmd sync "+src+" "+dest
                os.system(cmd)
            else:
                sys.exit()


# data should be of the format of json
def json_validator(filename, skip_errors=False):
#Try to open an load the json file and test if it comes up with any errors
    try:
        with open(filename,'r') as f:
            data = json.load(f)
    except KeyError as error:
        print("invalid key in JSON")
        #if the json comes up with any errors, the program will exit
        if not skip_errors:
            sys.exit()
    #If everything works, the json data will be returned
    except ValueError as error:
        print("invalid value in JSON")
        if not skip_errors:
            sys.exit()
    parse_data(data, args.verbose)

    return data


# check and parse the template input argument
def parse_template(template_str, testdebug=False, verbose=False):
    template_dict = {}
    comma_count = len([character for character in template_str if character == ','])
    equal_count = len([character for character in template_str if character == '='])

    if equal_count == (comma_count + 1):
        pairs = template_str.split(',')
        for pair in pairs:
            key,value = pair.split('=')
            template_dict[key] = value
    else:
        print("There is not an even split of commas and equal signs within this template input: " + template_str)
        print("The --template argument takes its argument in the format: 'A=B,C=D,E=F'" + template_str)
        print("Exiting.")
        sys.exit()

    return template_dict

#defines variables to hold the argparse information so that
#they can be called later in the for loop
parser = get_parser()
args = parser.parse_args()


### START HERE ###
json_file = args.jsonpath[0]
json_validator(json_file, args.skip_errors)
