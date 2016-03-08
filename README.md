# pyrocopy

pyrocopy is a suite of advanced file utility functions for efficiently copying all or part of a directory tree. It can be used as a module in your own application or run standalone.

## Main Features
* Mirror Mode
* Sync Mode (bi-directional copy)
* Regular expression based filename and directory matching
* Configurable maximum tree depth traversal
* Detailed operation statistics

## Contents
* [Installation](#Installation)
* [Using pyrocopy command line tool](#Using-pyrocopy-command-line-tool)
    * File Selection
    * Depth Selection
    * Examples
    * Reference
* [Using pyrocopy as a module](#Using-pyrocopy-as-a-module)
    * [File Selection](#File-Selection)
    * [Depth Selection](#Depth-Selection)
    * [Function Results](#Function-Results)
    * [Examples](#Examples)
    * [Reference](#Reference)

## Installation
pyrocopy can be easily installed with **pip** using the following command:

```
pip install pyrocopy
```

## Using pyrocopy command line tool
```
pyrocopy [-h] [--mirror | --move | --sync] [-f] [--nostat]
         [-if INCLUDEFILES] [-id INCLUDEDIRS] [-xf EXCLUDEFILES]
         [-xd EXCLUDEDIRS] [-l LEVEL] [-fl] [-q | -v] [--version]
         source destination
```

In addition to being used as a Python module, pyrocopy can be used as a standalone command line tool. The command line tool offers the same four copy modes as the module (**copy**, **mirror**, **move** and **sync**) with the default mode being **copy**.

The command line tool also provides detailed information about the running operation, including real-time progress bars. The output of the tool is configurable if you need more or less information using the *-v* and *-q* options respectively.

### File Selection
The tool can be instructed to limit the selection of files and directories to be copied by specifying a list of regular expressions. There are two types of file selection lists that can be specified; *inclusion* and *exclusion*.

The *--includefiles* (*-if*) option allows you to specify a regex pattern that will only copy files whose name matches the pattern. More than one pattern can be provided by adding an additional *--includefiles* option to the command line.

```
> pyrocopy --includefiles "pattern1" --includefiles "pattern2" /my/source/path /my/dest/path
```

The *--includedirs* (*-id*) option allows you to specify a regex pattern that will only copy directories whose name matches the pattern. Again, more than one pattern can be provided by adding an additional *--includedirs* option. This option can be used in addition to *--includefiles*.

```
> pyrocopy --includedirs "dirToInclude" /my/source/path /my/dest/path
```

The *--excludefiles* (*-xf*) option specifies a regex pattern that will skip any file whose name matches the pattern. This option is mutually exclusive to *--includefiles* and will have no effect if specified in addition to that option.

```
> pyrocopy --excludefiles "toExclude" /my/source/path /my/dest/path
```

The *--excludedirs* (*-xd*) option specifies a regex pattern that will skip any file whose name matches the pattern. This option is mutually exclusive to *--excludedirs* and will have no effect if specified in addition to that option.

### Depth Selection
In addition to filename and directory matching it is possible to define the maximum depth of the source tree that will be traversed. This provides the ability to perform shallow copies or deep copies of an arbitrary length. Furthermore, the tree can be traversed in reverse making it possible to only copy the files and directories contained in the furthest nodes of the tree.

This is accomplished with the *--level* option and specifying an integer value that counts the depth level away from the source root (or furthest node if using inverse depth). Specifying a value of **0** will traverse the entire source tree and is the default option. A positive value will copy the maximum depth reached from the top of the source tree with level 1 being the root of the source path provided. A negative value will copy in reverse, starting at the furthest node in the source tree and counting up towards the root. Therefore a value of -1 will copy only those files at the furthest subdirectory of the source path.

### Examples
#### Simple Copy
The following will copy one directory tree to another, skipping any existing files with the same path/name that are newer in the destination than the source.

```
> pyrocopy /my/src/path /my/dest/path
```

#### Copy with Inclusions
The following copies any filename in the source tree that has a name starting with 'myFile' followed by a number. To match the desired form the regular expression 'myFile[0-9]+\\..\*' is used. Note that '\\..\*' is required to properly match file extensions.

```
> pyrocopy --if "myFile[0-9]+\..*" /my/src/path /my/dest/path
```

#### Mirror with Exclusions
The following mirrors the source tree to the destination but excludes any directory with the name '.ignore'.

```
> pyrocopy --mirror --xd "\.ignore" /my/src/path /my/dest/path
```

#### Shallow Copy
Adding the 'level' argument with a value of 1 will copy only those files in the immediate source directory, skipping all subdirectories.

```
> pyrocopy --level 1 /my/src/path /my/dest/path
```

#### Inverse Shallow Copy
The inverted shallow copy duplicates the files at the furthest node of the source tree into the destination, creating all necessary subdirectories along the way.

To illustrate this behavior take the following source tree.
```
/PathA
    FileA1.txt
    /SubPathA1
        FileSubPathA1.txt
        /SubPathA2
            FileSubPathA2.txt
```

Using the following code will copy only FileSubPathA2.txt to the destination by adding the 'level' argument with a value of -1.

```
> pyrocopy --level -1 /PathA /PathB
```

The resulting destination tree looks like the following.
```
/PathB
    /SubPathA1
        /SubPathA2
            FileSubPathA2.txt
```

#### More Inverse Copy
Expanding on the previous example if we change the specified level from -1 to -2 we get a resulting file tree that copies both FileSubPathA2.txt and FileSubPathA1.txt. The code for this is as follows.

```
> pyrocopy --level -2 /PathA /PathB
```

With the destination tree looking like the following.
```
/PathB
    /SubPathA1
        FileSubPathA1.txt
        /SubPathA2
            FileSubPathA2.txt
```

### Reference
```usage: pyrocopy [-h] [--mirror | --move | --sync] [-f] [--nostat]
                [-if INCLUDEFILES] [-id INCLUDEDIRS] [-xf EXCLUDEFILES]
                [-xd EXCLUDEDIRS] [-l LEVEL] [-fl] [-q | -v] [--version]
                source destination

A robust file copying utility.

positional arguments:
  source                The path to copy contents from
  destination           The path to copy contents to

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit

copy mode:
  --mirror              Creates an exact copy of source to the destination
                        removing any files or directories in destination not
                        also contained in source.
  --move                Moves all files and directories from source to
                        destination (delete from source after copying).
  --sync                Performs a bi-directional copy of the contents of
                        source and destination to contain the exact same set
                        of files and directories in both locations.

copy options:
  -f, --force           Overwrites all files in destination from source even
                        if newer.
  --nostat              Do not copy file stats (mode bits, atime, mtime,
                        flags)

selection options:
  -if INCLUDEFILES, --includefiles INCLUDEFILES
                        A list of regular expressions for file inclusions
  -id INCLUDEDIRS, --includedirs INCLUDEDIRS
                        A list of regular expressions for directory inclusions
  -xf EXCLUDEFILES, --excludefiles EXCLUDEFILES
                        A list of regular expressions for file exclusions
  -xd EXCLUDEDIRS, --excludedirs EXCLUDEDIRS
                        A list of regular expressions for directory exclusions
  -l LEVEL, --level LEVEL
                        The maximum depth level to traverse during the copy,
                        starting from the source root. A negative value starts
                        from the furthest node from the source root.
  -fl, --followlinks    Traverses symbolic links as directories instead of
                        copying the link.

logging options:
  -q, --quiet           Shows less output during the operation.
  -v, --verbose         Shows more output during the operation.
```

## Using pyrocopy as a module

### Overview
There are four primary functions to pyrocopy; **copy**, **mirror**, **move** and **sync**. Each function takes the same set of arguments and will return a dictionary containing statistics about the operation.

### File Selection
The first key principle of pyrocopy is to provide a robust set of file selection features so that users can operate only on the files and directories they need. Each function offers the ability to specify separate lists of files or directories to include or exclude. Regular expressions are used to match file names and directories instead of wildcard based matching (e.g. '*.txt').

### Depth Selection
In addition to filename and directory matching it is possible to define the maximum depth of the source tree that will be traversed. This provides the ability to perform shallow copies or deep copies of an arbitrary length. Furthermore, the tree can be traversed in reverse making it possible to only copy the files and directories contained in the furthest nodes of the tree.

### Function Results
The four primary functions of pyrocopy (copy, mirror, move and sync) all return a dictionary containing statistics about the operation executed. Additionally, when the detailedResults argument is set to True an additional set of information is included in the results to aid in your application use.

The list of statistics are:

Statistics [copy, mirror, sync]
* filesCopied
* filesFailed
* filesSkipped
* dirsCopied
* dirsFailed
* dirsSkipped
* filesCopiedList [requires detailedResults]
* filesFailedList [requires detailedResults]
* filesSkippedList [requires detailedResults]
* dirsCopiedList [requires detailedResults]
* dirsFailedList [requires detailedResults]
* dirsSkippedList [requires detailedResults]

Statistics [move]
* filesMoved
* filesFailed
* filesSkipped
* dirsMoved
* dirsFailed
* dirsSkipped
* filesMovedList [requires detailedResults]
* filesFailedList [requires detailedResults]
* filesSkippedList [requires detailedResults]
* dirsMovedList [requires detailedResults]
* dirsFailedList [requires detailedResults]
* dirsSkippedList [requires detailedResults]

### Examples
#### Simple Copy
The following will copy one directory tree to another, skipping any existing files with the same path/name that are newer in the destination than the source.

```python
from pyrocopy import pyrocopy

results = pyrocopy.copy(source, destination)
```

#### Copy with Inclusions
The following copies any filename in the source tree that has a name starting with 'myFile' followed by a number. To match the desired form the regular expression 'myFile[0-9]+\\..\*' is used. Note that '\\..\*' is required to properly match file extensions.

```python
from pyrocopy import pyrocopy

results = pyrocopy.copy(source, destination, includeFiles=['myFile[0-9]+\..*'])
```

#### Mirror with Exclusions
The following mirrors the source tree to the destination but excludes any directory with the name '.ignore'.

```python
from pyrocopy import pyrocopy

results = pyrocopy.mirror(source, destination, excludeDirs=['\.ignore'])
```

#### Shallow Copy
Adding the 'level' argument with a value of 1 will copy only those files in the immediate source directory, skipping all subdirectories.

```python
from pyrocopy import pyrocopy

results = pyrocopy.copy(source, destination, level=1)
```

#### Inverse Shallow Copy
The inverted shallow copy duplicates the files at the furthest node of the source tree into the destination, creating all necessary subdirectories along the way.

To illustrate this behavior take the following source tree.
```
/PathA
    FileA1.txt
    /SubPathA1
        FileSubPathA1.txt
        /SubPathA2
            FileSubPathA2.txt
```

Using the following code will copy only FileSubPathA2.txt to the destination by adding the 'level' argument with a value of -1.

```python
from pyrocopy import pyrocopy

results = pyrocopy.copy("/pathA", destination, level=-1)
```

The resulting destination tree looks like the following.
```
/PathB
    /SubPathA1
        /SubPathA2
            FileSubPathA2.txt
```

#### More Inverse Copy
Expanding on the previous example if we change the specified level from -1 to -2 we get a resulting file tree that copies both FileSubPathA2.txt and FileSubPathA1.txt. The code for this is as follows.

```python
from pyrocopy import pyrocopy

results = pyrocopy.copy("/pathA", destination, level=-2)
```

With the destination tree looking like the following.
```
/PathB
    /SubPathA1
        FileSubPathA1.txt
        /SubPathA2
            FileSubPathA2.txt
```

### Reference
#### pyrocopy.copy
```python
def copy(src, dst, includeFiles=None, includeDirs=None, excludeFiles=None, excludeDirs=None, level=0,
         followLinks=False, forceOverwrite=False, preserveStats=True, detailedResults=False):
```
Copies all files and folders from the given source directory to the destination.

###### src:string
The source path to copy from
###### dst:string
The destination path to copy to
###### includeFiles:array
A list of regex patterns of files to include during the operation. Files not matching at least one pattern in the include list will be skipped.
###### includeDirs:array
A list of regex patterns of directory names to include during the operation. Directories not matching at least one pattern in the include list will be skipped.
###### excludeFiles:array
A list of regex patterns of files to exclude during the operation.
###### excludeDirs:array
A list of regex patterns of directory names to exclude during the operation.
###### level:int
The maximum depth to traverse in the source directory tree.

A value of 0 traverses the entire tree.
A positive value traverses N levels from the top with value 1 being the source root.
A negative value traverses N levels from the bottom of the source tree.
###### followLinks:bool
Set to true to traverse through symbolic links.
###### forceOverwrite:bool
Set to true to overwrite destination files even if they are newer.
###### preserveStats:bool
Set to True to copy the source file stats to the destination.
###### detailedResults:bool
Set to True to include additional details in the results containing a list of all files and directories that were skipped or failed during the operation.
###### return:dict
Returns a dictionary containing the following stats:
    'filesCopied':int, 'filesFailed':int, 'filesSkipped':int, 'dirsCopied':int, 'dirsFailed':int, 'dirsSkipped':int
If detailedResults is set to True also includes the following:
    'filesCopiedList':list, 'filesFailedList':list, 'filesSkippedList':list,
    'dirsCopiedList':list, 'dirsFailedList':list, 'dirsSkippedList':list

#### pyrocopy.mirror
```python
def mirror(src, dst, includeFiles=None, includeDirs=None, excludeFiles=None, excludeDirs=None, level=0,
         followLinks=False, forceOverwrite=False, preserveStats=True, detailedResults=False):
```
Creates an exact copy of the given source to the destination. Copies all files and directories from source to the
destination and removes any file or directory present in the destination that is not also in the source.

###### src:string
The source path to copy from
###### dst:string
The destination path to copy to
###### includeFiles:array
A list of regex patterns of files to include during the operation. Files not matching at least one pattern in the include list will be skipped.
###### includeDirs:array
A list of regex patterns of directory names to include during the operation. Directories not matching at least one pattern in the include list will be skipped.
###### excludeFiles:array
A list of regex patterns of files to exclude during the operation.
###### excludeDirs:array
A list of regex patterns of directory names to exclude during the operation.
###### level:int
The maximum depth to traverse in the source directory tree.

A value of 0 traverses the entire tree.
A positive value traverses N levels from the top with value 1 being the source root.
A negative value traverses N levels from the bottom of the source tree.
###### followLinks:bool
Set to true to traverse through symbolic links.
###### forceOverwrite:bool
Set to true to overwrite destination files even if they are newer.
###### preserveStats:bool
Set to True to copy the source file stats to the destination.
###### detailedResults:bool
Set to True to include additional details in the results containing a list of all files and directories that were skipped or failed during the operation.
###### return:dict
Returns a dictionary containing the following stats:
    'filesCopied':int, 'filesFailed':int, 'filesSkipped':int, 'dirsCopied':int, 'dirsFailed':int, 'dirsSkipped':int
If detailedResults is set to True also includes the following:
    'filesCopiedList':list, 'filesFailedList':list, 'filesSkippedList':list,
    'dirsCopiedList':list, 'dirsFailedList':list, 'dirsSkippedList':list

#### pyrocopy.move
```python
def move(src, dst, includeFiles=None, includeDirs=None, excludeFiles=None, excludeDirs=None, level=0,
         followLinks=False, forceOverwrite=False, preserveStats=True, detailedResults=False):
```
Moves all files and folders from the given source directory to the destination.

###### src:string
The source path to move from
###### dst:string
The destination path to move to
###### includeFiles:array
A list of regex patterns of files to include during the operation. Files not matching at least one pattern in the include list will be skipped.
###### includeDirs:array
A list of regex patterns of directory names to include during the operation. Directories not matching at least one pattern in the include list will be skipped.
###### excludeFiles:array
A list of regex patterns of files to exclude during the operation.
###### excludeDirs:array
A list of regex patterns of directory names to exclude during the operation.
###### level:int
The maximum depth to traverse in the source directory tree.

A value of 0 traverses the entire tree.
A positive value traverses N levels from the top with value 1 being the source root.
A negative value traverses N levels from the bottom of the source tree.
###### followLinks:bool
Set to true to traverse through symbolic links.
###### forceOverwrite:bool
Set to true to overwrite destination files even if they are newer.
###### preserveStats:bool
Set to True to copy the source file stats to the destination.
###### detailedResults:bool
Set to True to include additional details in the results containing a list of all files and directories that were skipped or failed during the operation.
###### return:dict
Returns a dictionary containing the following stats:
    'filesMoved', 'filesFailed', 'filesSkipped', 'dirsMoved', 'dirsFailed', 'dirsSkipped'
If detailedResults is set to True also includes the following:
    'filesMovedList':list, 'filesFailedList':list, 'filesSkippedList':list,
    'dirsMovedList':list, 'dirsFailedList':list, 'dirsSkippedList':list

#### pyrocopy.sync
```python
def sync(src, dst, includeFiles=None, includeDirs=None, excludeFiles=None, excludeDirs=None, level=0,
         followLinks=False, forceOverwrite=False, preserveStats=True, detailedResults=False):
```
Synchronizes all files and folders between the two given paths.

###### src:string
The source path to copy from
###### dst:string
The destination path to copy to
###### includeFiles:array
A list of regex patterns of files to include during the operation. Files not matching at least one pattern in the include list will be skipped.
###### includeDirs:array
A list of regex patterns of directory names to include during the operation. Directories not matching at least one pattern in the include list will be skipped.
###### excludeFiles:array
A list of regex patterns of files to exclude during the operation.
###### excludeDirs:array
A list of regex patterns of directory names to exclude during the operation.
###### level:int
The maximum depth to traverse in the source directory tree.

A value of 0 traverses the entire tree.
A positive value traverses N levels from the top with value 1 being the source root.
A negative value traverses N levels from the bottom of the source tree.
###### followLinks:bool
Set to true to traverse through symbolic links.
###### forceOverwrite:bool
Set to true to overwrite destination files even if they are newer.
###### preserveStats:bool
Set to True to copy the source file stats to the destination.
###### detailedResults:bool
Set to True to include additional details in the results containing a list of all files and directories that were skipped or failed during the operation.
###### return:dict
Returns a dictionary containing the following stats:
    'filesCopied':int, 'filesFailed':int, 'filesSkipped':int, 'dirsCopied':int, 'dirsFailed':int, 'dirsSkipped':int
If detailedResults is set to True also includes the following:
    'filesCopiedList':list, 'filesFailedList':list, 'filesSkippedList':list,
    'dirsCopiedList':list, 'dirsFailedList':list, 'dirsSkippedList':list
    
#### pyrocopy.mkdir
```python
def mkdir(path):
```
Creats a new directory at the specified path. This function will create all parent directories that are missing in the
given path.
##### path:string
The path of the new directory to create.
##### return:dict
Returns True if the directory was successfully created, otherwise False.
