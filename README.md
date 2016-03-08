# pyrocopy

pyrocopy is a suite of advanced file utility functions for efficiently copying all or part of a directory tree. It can be used as a module in your own application or run standaone.

##Main Features
* Mirror Mode
* Sync Mode (bi-directional copy)
* Regular expression based filename and directory matching
* Configurable maximum tree depth traversal
* Detailed operation statistics

## Installation
pyrocopy can be easily installed using pip with the following command:

```
pip install pyrocopy
```
## Using pyrocopy as a module

### Overview
There are four primary functions to pyrocopy; copy, mirror, move and sync. Each function takes the same set of arguments and will return a dictionary containing statistics about the operation.

#### File Selection
The first key principle of pyrocopy is to provide a robust set of file selection features so that users can operate only on the files and directories they need. Each function offers the ability to specify separate lists of files or directories to include or exclude and uses regular expressions instead to match the names instead of wildcard based matching (e.g. '*.txt') used by most file copy utilities.

#### Depth Selection
In addition to filename and directory matching it is possible to define the maximum depth of the source tree that will be traversed. This provides the ability to perform shallow copies or deep copies of an arbitrary length. Furthermore, the tree can be traversed in reverse making it possible to only copy the files and directories contained in the furthest nodes of the tree.

#### Function Results
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
#### Simply Copy
The following will perform a simply copy of one directory tree to another, skipping any existing files with the same path/name that are newer in the destination than the source.

```python
from pyrocopy import pyrocopy

results = pyrocopy.copy(source, destination)
```

#### Copy with Inclusions
The following copies any filename in the source tree that has a name starting with 'myFile' followed by N number. To match the desired form the regular expression 'myFile[0-9]+\..*' is used. '\..*' is required to properly match file extensions.

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
In order to perform a shallow copy with only the files in the source and no subfolders simply add the 'level' argument with a value of 1.

```python
from pyrocopy import pyrocopy

results = pyrocopy.copy(source, destination, level=1)
```

### Reverse Shallow Copy
The reverse shallow copy duplicates the files at the furthest node of the source into the destination, creating all necessary subdirectories along the way.

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

The destination tree with look like the following.
```
/PathB
    /SubPathA1
        /SubPathA2
            FileSubPathA2.txt
```

#### More Reverse Copy
Expanding on the previous example if we change the specified level from -1 to -2 we get a resulting tree that copies both FileSubPathA2.txt and FileSubPathA1.txt. The code for this is as follows.

```python
from pyrocopy import pyrocopy

results = pyrocopy.copy("/pathA", destination, level=-2)
```

The destination tree with then look like the following.
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
