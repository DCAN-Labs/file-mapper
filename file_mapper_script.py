#! /usr/bin/env python3
# USAGE:
#   ./Mover.py <JSON-file>

#import the different python libraries
import os, sys
import json
import argparse
import shutil
import pprint

#gives a description over the purpose of the program
PROG = 'File Mapper'
VERSION = '1.1.0'

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
    #gives the three choices as an argument that the user can pass through
    #to manipulate the path of the json file
    parser.add_argument('-a', '--action', dest='action', required=False, default='copy',
                        choices = ['copy', 'move', 'symlink', 'move+symlink'],
                        help="""The three different actions of the script which
                        copies moves or symlinks, with a default of copy.""")
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

#big function that parses the entire JSON file
def parse_data(data, verbose=False, testdebug=False):
    non_specials_list = []
    #Checks for source and destination arguments in the JSON
    for element in data.keys():
        if element not in ['SOURCE', 'DESTINATION']:
            non_specials_list.append(element)
        #If sourcepath exists the append it to the destination value and overwrite
    for key in non_specials_list:
        if args.sourcepath != None:
            if verbose:
                print("A sourcepath arguement exists")
            source = os.path.join(args.sourcepath[0], key)
            if 'SOURCE' in data:
                if verbose:
                    print('Optional SOURCE argument: '+ args.sourcepath[0] +
                    ' overrules source: ' + data['SOURCE'].encode('ascii', 'ignore'))
        elif 'SOURCE' in data:
            if verbose:
                print("Source already exists in json data")
            source = os.path.join(data['SOURCE'],key)
        #If the destination path arguement exists then append to the key and overwrites the preexisting argument
        if args.destpath != None:
            if verbose:
                print("A destination path argument exists")
            destination = os.path.join(args.destpath[0], data[key])
            if 'DESTINATION' in data:
                if verbose:
                    print('Optional DESTINATION argument: '+ args.destpath[0] +
                    ' overrules destination: ' + data['DESTINATION'].encode('ascii', 'ignore'))
        #If the destination arguement exists then append it to the key value
        elif "DESTINATION" in data:
            if verbose:
                print("Destination already exists in json data")
            destination = os.path.join(data['DESTINATION'], data[key])
        else:
            #If neither exists then use preexisting values
            if verbose:
                print("DESTINATION not provided, using prexisting values in JSON")
            destination = data[key]
        #check if the path in the json data actually exists
        if os.path.exists(source) and os.path.isfile(source):
            dirname = os.path.dirname(destination)
            # make a directory based on the key in the json file
            if os.path.isfile(destination):
                if not args.overwrite:
                    if verbose or testdebug:
                        print("Destination file already exists: " + destination.encode('ascii', 'ignore'))
                elif args.overwrite:
                    do_action(source, destination, args.action,
                    overwrite=args.overwrite, testdebug=args.testdebug)
                    if verbose:
                        print("File has been overwritten".encode('ascii', 'ignore'))
                elif os.path.exists(dirname):
                    if verbose:
                        print("Path already exists: " + dirname.encode('ascii', 'ignore'))
            elif os.path.isdir(os.path.dirname(destination)):
                do_action(source, destination, args.action, testdebug = args.testdebug)
            else:
                os.makedirs( dirname )
                if verbose:
                    print("Path has been made: " + dirname.encode('ascii', 'ignore'))
                do_action(source, destination, args.action, testdebug = args.testdebug)




#Decides what to do based on the action chosen by the user
def do_action(src, dest, action, overwrite = False, testdebug = False, relsym = False):
    if overwrite:
        overwrite_string = 'overwrite '
    else:
        overwrite_string = ''
        #If testdebug mode is present then a string will be constructed based on the arguments provided by the user
        if testdebug:
            print(overwrite_string + action + ': ' + src + ' -> ' + dest.encode('ascii', 'ignore'))
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
                os.symlink(src, dest)
            #moves the file from one directory to another AND symlinks it back to its source
            elif action == "move+symlink":
                if overwrite:
                    os.remove(dest)
                shutil.move(src, dest)
                os.symlink(dest, src)
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



#defines variables to hold the argparse information so that
#they can be called later in the for loop
parser = get_parser()
args = parser.parse_args()


### START HERE ###
json_file = args.jsonpath[0]
json_validator(json_file, args.skip_errors)
