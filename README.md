# File Mapper

An easy way to copy/move/symlink files from one directory to another all-in-one.

## Intended Purpose

This program is designed to help users copy, move, or symlink files from one directory to another using a JSON file as input.  The JSON keys being the source of the files and the JSON values being the desired destination path.  This program has been designed to move important files from a large dataset and would be applicable in any BIDS datasets or other renaming/mapping utility.

## Installation

* Use python 3.7
* Clone file-mapper repo locally

## Usage of Script

1. Make sure that the JSON file that is being interpreted takes paths as its keys and values.

  * If the keys/values are relative paths, make sure a SOURCE key and a DESTINATION key exist or are passed into the script as options so that their full paths can be resolved.
  * If the keys/values are absolute paths the file will run normally.

2. To run the file, call

    ```shell
    python file_mapper_script.py [absolute path to the JSON file] -a [one of three actions: copy, move, or symlink]
    ```

  * The absolute path to the JSON file needs to be provided as a positional argument so the program can locate the file to process.
  * The -a (--action) option allows the user to choose between moving, copying, symlinking, or using the s3cmd to map from an s3 bucket ("S3cmd").  
      - The default is to copy
  * If the path has already been made, and an overwrite is needed, add the -o (--overwrite) flag.
  * If the overwrite flag is not provided and the file already exists then the console wil display: `Destination file already exists: [absolute path to the file]`  
  * If overwrite is successfull then the console will display: `file has been overwritten`
  * If errors are to be skipped, the -s (--skip-errors) flag will skip errors and proceed to run the program.  
  * If a custom SOURCE or DESTINATION for the JSON file and its contents is required:

      - The -sp (--sourcepath) tag and the -dp (--destpath) tag allows the user to input a custom SOURCE or DESTINATION
      - The provided roots will overwrite the given roots in the JSON file and provide this message: `Optional DESTINATION argument: [path of the provided dest] overrules destination: [initial given dest]`

  * A verbose tag (-vb (--verbose)) can be used to display verbose print statements when the program is run.

      - Without the -vb tag the program will run without displaying any messages to the console, under the philosophy "Succeed silently, fail loudly."

  * The testdebug flag (-td (--testdebug)) can be used to display to the console what the code does without performing any actions

      - The -td flag works with overwrite statements as well, displaying `overwrite_string + action + ': ' + src + ' -> ' + dest`

  * If the keys/values are absolute paths the file will run normally.

3. If the file runs without error, the console will display a message for each path made: `Path has been made: (absolute path of file created)`

  * If the JSON is not properly written the console will display an error message: `Invalid json: error`

## Example 1: A SOURCE and DESTINATION in the JSON

Call function with relative path to json and action for mapping along verbose mode to show print statements.

```
user@server:~/file-mapper$ ./file_mapper_script.py ./testing.json -a copy -vb

# The SOURCE is included in the json as a key: value path
Source already exists in json data
DESTINATION not provided, using prexisting values in JSON

# Message to show that the path has been made
Path has been made: /example/mapped/path
Source already exists in json data
DESTINATION not provided, using prexisting values in JSON
Source already exists in json data
DESTINATION not provided, using prexisting values in JSON
```

## Example 2: SOURCE and DESTINATION passed in on the command line with the TEMPLATE option

File mapping in silent mode using the overwrite and skip errors flags as well as specifying the root source path and root destination path for mapped files.

```
user@server:~/file-mapper$ ./file_mapper_script.py ./example2.json -a copy -o -s -sp /folder/containing/source/files/ -dp /folder/to/house/destination/files/ -t SUBJECT=NDARSOMETHING,SESSION=122months,PIPELINE=infant-abcd-bids-pipeline"
```
