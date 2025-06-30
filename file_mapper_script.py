#! /usr/bin/env python
#
# Requires Python 3
# BASIC USAGE:
#   ./file_mapper_script.py <JSON-file>
#

#import the different python libraries
import argparse
import json
import os
import shutil
import sys

#gives a description over the purpose of the program
PROG = 'File Mapper'
VERSION = '1.4.0'

program_desc = """%(prog)s v%(ver)s:
Script to make a new directory and map files from a source directory. Files
can be copied or moved, or the script can make symbolic links.
""" % {'prog': PROG, 'ver': VERSION}


def get_parser():
    #sets a variable equal to the argparse function which lets a user input
    #choices
    parser = argparse.ArgumentParser(description=program_desc, prog=PROG)

    #gives the absolute path to the json file
    parser.add_argument('jsonpath', nargs=1,
                    help="""Absolute path to the required JSON.""")

    #gives the choices as an argument that the user can pass through
    #to manipulate the path of the json file
    parser.add_argument('-a', '--action', dest='action', required=False, default='copy',
                        choices = ['copy', 'move', 'symlink', 'move+symlink'],
                        help="""Choose between moving, copying, or symlinking between
                        the source and destination. Default: copy.""")

    parser.add_argument('-o', '--overwrite', dest='overwrite', required=False,
                        default=False, action = 'store_true',
                        help="""This allows new files to be created whether or not
                        they already exist.
                        If a path already exists, and this flag was not provided, the
                        console will display a message that the path already exists
                        and the file will not be copied.
                        If a path already exists and this flag was used, the console
                        will display a message that the file was overwritten.
                        """)

    parser.add_argument('-s', '--skip-errors', dest='skip_errors',
                        required=False, default=False, action= 'store_true',
                        help="""This skips over the errors in a JSON file so
                        that the other keys/values can be properly read.
                        """)

    parser.add_argument('-sp', '--sourcepath', nargs=1, default=None, required=False,
                        help="""Provides the absolute path to the source of the file
                        being copied/moved/symlinked.
                        """)

    parser.add_argument('-dp', '--destpath', nargs=1, default=None, required=False,
                        help="""Provides the absolute path to the destination of the
                        file being copied/moved/symlinked.
                        """)

    parser.add_argument('-t', '--template', nargs=1, default=None, required=False,
                        help="""A no-spaces-allowed, comma-separated
                        list of template fill-ins to replace fields in your JSON of
                        the format: 'TEMPLATE1=REPLACEMENT1,TEMPLATE2=REPLACEMENT2,...'.
                        For example let's say you want to replace a {SUBJECT} and
                        {SESSION} template variable you would use:
                        -t 'SUBJECT=sub-01,SESSION=ses-baseline'
                        """)

    parser.add_argument('-td', '--testdebug', dest='testdebug', required=False,
                        default=False, action='store_true',
                        help="""Display what the code would do, using the other
                        options provided, without performing the actions.
                        """)

    parser.add_argument('-vb', '--verbose', dest='verbose', required=False,
                        default=False, action='store_true',
                        help="""Without this option, the program will run without
                        displaying any messages to the console, under the philosophy
                        'Succeed silently, fail loudly.'
                        """)

    parser.add_argument('-relsym', '--relative-symlink', dest='relative_symlink',
                        required=False, default=False, action='store_true',
                        help="""Allows user to chose whether or not the symlink
                        being created is a relative path so that root
                        directories can be moved without the link breaking.
                        """)

    parser.add_argument('-sc', '--sidecars', dest='sidecars',
                        required=False, default=False, action='store_true',
                        help="""Also copy/move/symlink the corresponding
                        json sidecars""")

    return parser


def map_sidecars(source, destination):
    ''' Return name of json sidecars to be copied/symlinked etc

    Args:
        source (str): full path to source file
        destination (str): full path to destination
    Returns:
        json_src (str): full path to source json file
        json_dest (str): fill path to destination json file
    '''

    replace = [".nii.gz", ".nii"]

    for repl in replace:
        if source.endswith(repl):
            json_src = source.replace(repl, ".json")
            json_dest = destination.replace(repl, ".json")
            break

    return json_src, json_dest


#big function that parses the entire JSON file
def parse_data(contents, verbose=False, testdebug=False):
    data = {}
    for source, destination in contents.items():
        if '{#}' in source and '{#}' in destination:
            for i in range(100):
                num_zeropad_1 = '{:01d}'.format(i)
                num_zeropad_2 = '{:02d}'.format(i)
                num_zeropad_3 = '{:03d}'.format(i)
                zeropads = list(set([num_zeropad_1, num_zeropad_2, num_zeropad_3]))
                for zeropad in zeropads:
                    source_temp = source.replace('{#}', zeropad)
                    destination_temp = destination.replace('{#}', zeropad)
                    data[source_temp] = destination_temp
        else:
            data[source] = destination

    #Checks for source and destination arguments in the JSON
    non_specials_list = []
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
        else:
            if verbose:
                print("No source provided. Defaulting to key from json data")
            source = key
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
                    if args.sidecars and ( source.endswith('.nii') or source.endswith('.nii.gz') ):
                        json_src, json_dest = map_sidecars(source, destination)
                        if os.path.isfile(json_src):
                            do_action(json_src, json_dest, args.action,
                                      overwrite=args.overwrite,
                                      testdebug=args.testdebug,
                                      relsym=args.relative_symlink)
                    if verbose:
                        print("File has been overwritten")
                elif os.path.exists(dirname):
                    if verbose:
                        print("Path already exists: " + str(dirname))
            elif os.path.isdir(os.path.dirname(destination)):
                do_action(source, destination, args.action, testdebug=args.testdebug, relsym=args.relative_symlink)
                if args.sidecars and ( source.endswith('.nii') or source.endswith('.nii.gz') ):
                    json_src, json_dest = map_sidecars(source, destination)
                    if os.path.isfile(json_src):
                        do_action(json_src, json_dest, args.action,
                                  testdebug=args.testdebug,
                                  relsym=args.relative_symlink)
            else:
                os.makedirs( dirname )
                if verbose:
                    print("Path has been made: " + str(dirname))
                do_action(source, destination, args.action, testdebug=args.testdebug, relsym=args.relative_symlink)
                if args.sidecars and ( source.endswith('.nii') or source.endswith('.nii.gz') ):
                    json_src, json_dest = map_sidecars(source, destination)
                    if os.path.isfile(json_src):
                        do_action(json_src, json_dest, args.action,
                                  testdebug=args.testdebug,
                                  relsym=args.relative_symlink)



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
