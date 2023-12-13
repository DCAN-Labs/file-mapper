# File Mapper

An easy way to copy/move/symlink files from one directory to another all-in-one.

## Intended Purpose

This program is designed to help users copy, move, or symlink files from one directory to another using a JSON file as input.  The JSON keys being the source of the files and the JSON values being the desired destination path.  This program has been designed to move important files from a large dataset and would be applicable in any BIDS datasets or other renaming/mapping utility.

## Installation

* Use python 3.7
* Clone file-mapper repo locally

## Usage of Script

```
usage: File Mapper [-h] [-a {copy,move,symlink,move+symlink}] [-o] [-s]
                   [-sp SOURCEPATH] [-dp DESTPATH] [-t TEMPLATE] [-td] [-vb]
                   [-relsym] [-sc]
                   jsonpath

File Mapper v1.4.0: Script to make a new directory and map files from a source
directory. Files can be copied or moved, or the script can make symbolic
links.

positional arguments:
  jsonpath              Absolute path to the required JSON.

optional arguments:
  -h, --help            show this help message and exit
  -a {copy,move,symlink,move+symlink}, --action {copy,move,symlink,move+symlink}
                        Choose between moving, copying, or symlinking between
                        the source and destination. Default: copy.
  -o, --overwrite       This allows new files to be created whether or not
                        they already exist. If a path already exists, and this
                        flag was not provided, the console will display a
                        message that the path already exists and the file will
                        not be copied. If a path already exists and this flag
                        was used, the console will display a message that the
                        file was overwritten.
  -s, --skip-errors     This skips over the errors in a JSON file so that the
                        other keys/values can be properly read.
  -sp SOURCEPATH, --sourcepath SOURCEPATH
                        Provides the absolute path to the source of the file
                        being copied/moved/symlinked.
  -dp DESTPATH, --destpath DESTPATH
                        Provides the absolute path to the destination of the
                        file being copied/moved/symlinked.
  -t TEMPLATE, --template TEMPLATE
                        A no-spaces-allowed, comma-separated list of template
                        fill-ins to replace fields in your JSON of the format:
                        'TEMPLATE1=REPLACEMENT1,TEMPLATE2=REPLACEMENT2,...'.
                        For example let's say you want to replace a {SUBJECT}
                        and {SESSION} template variable you would use: -t
                        'SUBJECT=sub-01,SESSION=ses-baseline'
  -td, --testdebug      Display what the code would do, using the other
                        options provided, without performing the actions.
  -vb, --verbose        Without this option, the program will run without
                        displaying any messages to the console, under the
                        philosophy 'Succeed silently, fail loudly.'
  -relsym, --relative-symlink
                        Allows user to chose whether or not the symlink being
                        created is a relative path so that root directories
                        can be moved without the link breaking.
  -sc, --sidecars       Also copy/move/symlink the corresponding json sidecars
```

NOTES:

1. Make sure that the JSON file that is being interpreted takes paths as its keys and values.

  * If the keys/values are relative paths, make sure a SOURCE key and a DESTINATION key exist or are passed into the script as options so that their full paths can be resolved.
  * If the keys/values are absolute paths the file will run normally.

2. If the file runs without error, the console will display a message for each path made: `Path has been made: (absolute path of file created)`

  * If the JSON is not properly written the console will display an error message: `Invalid json: error`

## Example 1: A SOURCE and DESTINATION in the JSON

Call function with relative path to json and action for mapping along verbose mode to show print statements.

```
user@server:~/file-mapper$ ./file_mapper_script.py ./testing.json -a copy -vb

# The SOURCE is included in the json as a key: value path
Source already exists in json data
DESTINATION not provided, using preexisting values in JSON

# Message to show that the path has been made
Path has been made: /example/mapped/path
Source already exists in json data
DESTINATION not provided, using preexisting values in JSON
Source already exists in json data
DESTINATION not provided, using preexisting values in JSON
```

## Example 2: SOURCE and DESTINATION passed in on the command line with the TEMPLATE option

File mapping in silent mode using the overwrite and skip errors flags as well as specifying the root source path and root destination path for mapped files.

```
user@server:~/file-mapper$ ./file_mapper_script.py ./example2.json -a copy
-o -s -sp /folder/containing/source/files/ -dp /folder/to/house/destination/files/
-t SUBJECT=NDARSOMETHING,SESSION=122months,PIPELINE=infant-abcd-bids-pipeline"
```
