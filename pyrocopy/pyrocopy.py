#!/usr/bin/env python
'''
Robust file utilities for Python inspired by Windows' robocopy.

Homepage: https://github.com/caskater4/pyrocopy

Copyright (C) 2016 Jean-Philippe Steinmetz

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import errno
import fnmatch
import logging
import os
import re
import stat
import sys

'''
The version of this script as an int tuple (major, minor, patch).
'''
__version__ = (0, 8, 0)

'''
The version of this script as a string. (e.g. '1.0.0')
'''
__version_str__ = '.'.join([str(__version__[0]), str(__version__[1]), str(__version__[2])])

'''
The logger used to report information and progress during operations.

The default log level is INFO.
'''
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

BUFFERSIZE_KIB = 16  # Buffer size in kiB for file-copy operations.

'''
Copies all files and folders from the given source directory to the destination.

:type src:string
:param src: The source path to copy from

:type dst:string
:param dst: The destination path to copy to

:type includeFiles:array
:param includeFiles: A list of regex and wildcard patterns of files to include during the operation.
                     Files not matching at least one pattern in the include list will be skipped.
                     Regex patterns must be prefixed with re:

:type includeDirs:array
:param includeDirs: A list of regex and wildcard patterns of directory names to include during the operation.
                    Directories not matching at least one pattern in the include list will be skipped.
                    Regex patterns must be prefixed with re:

:type excludeFiles:array
:param excludeFiles: A list of regex and wildcard patterns of files to exclude during the operation.
                     Regex patterns must be prefixed with re:

:type excludeDirs:array
:param excludeDirs: A list of regex and wildcard patterns of directory names to exclude during the operation.
                    Regex patterns must be prefixed with re:

:type level:int
:param level: The maximum depth to traverse in the source directory tree.
               A value of 0 traverses the entire tree.
               A positive value traverses N levels from the top with value 1 being the source root.
               A negative value traverses N levels from the bottom of the source tree.

:type followLinks:bool
:param followLinks: Set to true to traverse through symbolic links.

:type forceOverwrite:bool
:param forceOverwrite: Set to true to overwrite destination files even if they are newer.

:type preserveStats:bool
:param preserveStats: Set to True to copy the source file stats to the destination.

:type detailedResults:bool
:param detailedResults: Set to True to include additional details in the results containing a list of all files and
                        directories that were skipped or failed during the operation.

:rtype:dict
:return: Returns a dictionary containing the following stats:
         'filesCopied':int, 'filesFailed':int, 'filesSkipped':int, 'dirsCopied':int, 'dirsFailed':int, 'dirsSkipped':int
         If detailedResults is set to True also includes the following:
         'filesCopiedList':list, 'filesFailedList':list, 'filesSkippedList':list,
         'dirsCopiedList':list, 'dirsFailedList':list, 'dirsSkippedList':list
'''


def copy(src, dst, includeFiles=None, includeDirs=None, excludeFiles=None, excludeDirs=None, level=0,
         followLinks=False, forceOverwrite=False, preserveStats=True, detailedResults=False):
    # Always work with absolute paths
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)

    # Stats
    results = {}
    results['filesCopied'] = 0
    results['filesFailed'] = 0
    results['filesSkipped'] = 0
    results['dirsCopied'] = 0
    results['dirsFailed'] = 0
    results['dirsSkipped'] = 0
    if (detailedResults):
        results['filesCopiedList'] = []
        results['filesFailedList'] = []
        results['filesSkippedList'] = []
        results['dirsCopiedList'] = []
        results['dirsFailedList'] = []
        results['dirsSkippedList'] = []

    # Compile the provided regex patterns
    includeFilePatterns = []
    if (includeFiles != None):
        for pattern in includeFiles:
            if (pattern.startswith("re:")):
                includeFilePatterns.append(re.compile(pattern[3:]))
            else:
                includeFilePatterns.append(pattern)
    includeDirPatterns = []
    if (includeDirs != None):
        for pattern in includeDirs:
            if (pattern.startswith("re:")):
                includeDirPatterns.append(re.compile(pattern[3:]))
            else:
                includeDirPatterns.append(pattern)
    excludeFilePatterns = []
    if (excludeFiles != None):
        for pattern in excludeFiles:
            if (pattern.startswith("re:")):
                excludeFilePatterns.append(re.compile(pattern[3:]))
            else:
                excludeFilePatterns.append(pattern)
    excludeDirPatterns = []
    if (excludeDirs != None):
        for pattern in excludeDirs:
            if (pattern.startswith("re:")):
                excludeDirPatterns.append(re.compile(pattern[3:]))
            else:
                excludeDirPatterns.append(pattern)

    if (not _isSamePath(src, dst)):
        # Is the source path a file, directory or symlink?
        if (os.path.isfile(src) or (not followLinks and os.path.islink(src))):
            # Is the destination path a file name or directory?
            if (os.path.isdir(dst)):
                dst = os.path.join(dst, os.path.basename(src))

            # Copy the file
            result = _copyFile(src, dst, includeFilePatterns, excludeFilePatterns, forceOverwrite=forceOverwrite)
            if (result == 1):
                logger.info("Copied: %s => %s", src, dst)
                results['filesCopied'] += 1
                if (detailedResults):
                    results['filesCopiedList'].append(src)
            elif (result == 0):
                logger.info("Skipped: %s", src)
                results['filesSkipped'] += 1
                if (detailedResults):
                    results['filesSkippedList'].append(src)
            else:
                logger.error("Failed: %s => %s", src, dst)
                results['filesFailed'] += 1
                if (detailedResults):
                    results['filesFailedList'].append(src)
        elif (os.path.isdir(src)):
            # Make sure the destination exists to copy files to
            if (not os.path.isdir(dst)):
                mkdir(dst)

            # Determine the max depth.
            maxDepth = _getTreeDepth(src)

            # Traverse the tree and begin copying. Always traverse from the bottom up as this ensures we get the
            # desired behavior for file/dir inclusion patterns.
            for root, dirs, files in os.walk(src, topdown=False, followlinks=followLinks):
                relRoot = os.path.relpath(root, src)

                logger.debug("Processing Directory: %s", relRoot)

                # Is the root a symlink? Should we follow?
                if (os.path.islink(root) and not followLinks):
                    logger.info("Skipped: %s", relRoot)
                    results['dirsSkipped'] += 1
                    if (detailedResults):
                        results['dirsSkippedList'].append(relRoot)
                    continue

                # Exclude items not at the desired depth
                if (level != 0):
                    # Determine the current depth of relRoot
                    depth = 0
                    if (relRoot != '.'):
                        depth = relRoot.count(os.path.sep) + 1

                    # If traversing in reverse we need to subtract the max depth to get the relative level
                    if (level < 0):
                        depth = maxDepth - depth

                    # Now check the level
                    if (depth >= abs(level)):
                        logger.info("Skipped: %s", relRoot)
                        results['dirsSkipped'] += 1
                        if (detailedResults):
                            results['dirsSkippedList'].append(relRoot)
                        continue

                # Should the directory be traversed?
                if (relRoot != '.' and
                        not _checkShouldCopy(relRoot, False, includeDirPatterns, excludeDirPatterns)):
                    logger.info("Skipped: %s", relRoot)
                    results['dirsSkipped'] += 1
                    if (detailedResults):
                        results['dirsSkippedList'].append(relRoot)
                    continue

                # Make sure the root directory exists at the destination
                dstRoot = dst
                if (relRoot != '.'):
                    dstRoot = os.path.join(dst, relRoot)
                if (not os.path.isdir(dstRoot)):
                    mkdir(dstRoot)

                if (relRoot != '.'):
                    if (os.path.isdir(dstRoot)):
                        results['dirsCopied'] += 1
                        if (detailedResults):
                            results['dirsCopiedList'].append(relRoot)
                    else:
                        logger.exception("Failed: %s", relRoot)
                        results['dirsFailed'] += 1
                        if (detailedResults):
                            results['dirsFailedList'].append(relRoot)
                        continue

                for file in files:
                    filePath = os.path.join(relRoot, file)
                    srcFullPath = os.path.join(src, root, file)
                    dstFullPath = os.path.join(dst, filePath)

                    # Copy the file
                    result = _copyFile(srcFullPath, dstFullPath, includes=includeFilePatterns,
                                       excludes=excludeFilePatterns, forceOverwrite=forceOverwrite,
                                       preserveStats=preserveStats)
                    if (result == 1):
                        logger.info("Copied: %s => %s", filePath, dstFullPath)
                        results['filesCopied'] += 1
                        if (detailedResults):
                            results['filesCopiedList'].append(filePath)
                    elif (result == 0):
                        logger.info("Skipped: %s", filePath)
                        results['filesSkipped'] += 1
                        if (detailedResults):
                            results['filesSkippedList'].append(filePath)
                    else:
                        logger.error("Failed: %s => %s", filePath, dstFullPath)
                        results['filesFailed'] += 1
                        if (detailedResults):
                            results['filesFailedList'].append(filePath)
        else:
            logger.error("Source path is not valid: %s", src)
            results['filesFailed'] += 1
    else:
        logger.error("Cannot perform a copy to the same location.")
        results['dirsFailed'] += 1

    return results


'''
Creats a new directory at the specified path. This function will create all parent directories that are missing in the
given path.

:type path:string
:param path: The path of the new directory to create.

:rtype:bool
:return: Returns True if the directory was successfully created, otherwise False.
'''


def mkdir(path):
    if (os.path.exists(path)):
        return os.path.isdir(path)

    # Determine if the parent directory exists, if not attempt to create it
    pair = os.path.split(path)
    if (pair[0] != '' and not os.path.isdir(pair[0])):
        mkdir(pair[0])

    # Now does the parent directory exist?
    if (pair[0] != '' and not os.path.isdir(pair[0])):
        return False

    # Attempt to create the directory
    os.mkdir(path)

    logger.debug("Created: %s", path)

    return os.path.isdir(path)


'''
Creates an exact copy of the given source to the destination. Copies all files and directories from source to the
destination and removes any file or directory present in the destination that is not also in the source.

:type src:string
:param src: The source path to copy from

:type dst:string
:param dst: The destination path to copy to

:type includeFiles:array
:param includeFiles: A list of regex and wildcard patterns of files to include during the operation.
                     Files not matching at least one pattern in the include list will be skipped.
                     Regex patterns must be prefixed with re:

:type includeDirs:array
:param includeDirs: A list of regex and wildcard patterns of directory names to include during the operation.
                    Directories not matching at least one pattern in the include list will be skipped.
                    Regex patterns must be prefixed with re:

:type excludeFiles:array
:param excludeFiles: A list of regex and wildcard patterns of files to exclude during the operation.
                     Regex patterns must be prefixed with re:

:type excludeDirs:array
:param excludeDirs: A list of regex and wildcard patterns of directory names to exclude during the operation.
                    Regex patterns must be prefixed with re:

:type level:int
:param level: The maximum depth to traverse in the source directory tree.
               A value of 0 traverses the entire tree.
               A positive value traverses N levels from the top with value 1 being the source root.
               A negative value traverses N levels from the bottom of the source tree.

:type followLinks:bool
:param followLinks: Set to true to traverse through symbolic links.

:type forceOverwrite:bool
:param forceOverwrite: Set to true to overwrite destination files even if they are newer.

:type preserveStats:bool
:param preserveStats: Set to True to copy the source file stats to the destination.

:type detailedResults:bool
:param detailedResults: Set to True to include additional details in the results containing a list of all files and
                        directories that were skipped or failed during the operation.

:rtype:dict
:return: Returns a dictionary containing the following stats:
         'filesCopied':int, 'filesFailed':int, 'filesRemoved':int, 'filesSkipped':int, 'dirsCopied':int,
         'dirsFailed':int, 'dirsRemoved':int, 'dirsSkipped':int
         If detailedResults is set to True also includes the following:
         'filesCopiedList':list, 'filesFailedList':list, 'filesRemovedList':list, 'filesSkippedList':list,
         'dirsCopiedList':list, 'dirsFailedList':list, 'dirsRemovedList':list, 'dirsSkippedList':list
'''


def mirror(src, dst, includeFiles=None, includeDirs=None, excludeFiles=None, excludeDirs=None, level=0,
           followLinks=False, forceOverwrite=False, preserveStats=True, detailedResults=False):
    # Always work with absolute paths
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)

    # Attempt to copy everything
    results = copy(src, dst, includeFiles=includeFiles, includeDirs=includeDirs, excludeFiles=excludeFiles,
                   excludeDirs=excludeDirs, level=level, followLinks=followLinks, forceOverwrite=forceOverwrite,
                   preserveStats=preserveStats, detailedResults=True)

    # Add the additional stats not included by copy
    results['filesRemoved'] = 0
    results['dirsRemoved'] = 0
    if (detailedResults):
        results['filesRemovedList'] = []
        results['dirsRemovedList'] = []

    # Add the exclude files
    results['dirsSkippedList'] = []
    if excludeDirs != None:
        results['dirsSkippedList'] += excludeDirs

    results['filesSkippedList'] = []
    if excludeFiles != None:
        results['filesSkippedList'] += excludeFiles

    # Determine the max depth of src so that we don't go beyond that level in dst (if they're different)
    maxDepth = _getTreeDepth(src)

    # Now traverse through the destination and remove anything not also in source
    for root, dirs, files in os.walk(dst, topdown=False, followlinks=followLinks):
        relRoot = os.path.relpath(root, dst)

        # Make sure we are removing files/dirs only at the desired depth
        if (level != 0):
            # Determine the current depth of relRoot
            depth = 0
            if (relRoot != '.'):
                depth = relRoot.count(os.path.sep) + 1

            if (level < 0):
                depth = maxDepth - depth

            # Now check the level
            if (depth >= abs(level)):
                continue

        # Don't remove any dirs that are in the skipped or failed lists
        dirSkipped = False
        for skippedDir in results['dirsSkippedList']:
            if (relRoot == skippedDir):
                dirSkipped = True
                break
        if (not dirSkipped):
            for skippedDir in results['dirsFailedList']:
                if (relRoot == skippedDir):
                    dirSkipped = True
                    break

        if (not dirSkipped):
            # Go through the files in the directory and remove those not found in src and not skipped or failed
            for file in files:
                filePath = os.path.join(root, file)
                relFilePath = os.path.join(relRoot, file)

                # Was the file skipped or failed?
                fileSkipped = False
                for skippedFile in results['filesSkippedList']:
                    if (relFilePath == skippedFile):
                        fileSkipped = True
                        break
                if (not fileSkipped):
                    for failedFile in results['filesFailedList']:
                        if (relFilePath == failedFile):
                            fileSkipped = True
                            break

                if (not fileSkipped):
                    srcFilePath = os.path.join(src, relFilePath)
                    if (not os.path.exists(srcFilePath)):
                        try:
                            os.remove(filePath)
                            logger.info("Removed: %s", filePath)
                            results['filesRemoved'] += 1
                            if (detailedResults):
                                results['filesRemovedList'].append(relFilePath)
                        except (IOError, OSError):
                            logger.info("Remove failed: %s", relFilePath)
                            results['filesFailedList'].append(relFilePath)

            # Should the directory be deleted?
            srcRoot = os.path.join(src, relRoot)
            if (not os.path.exists(srcRoot)):
                dirlist = os.listdir(root)
                if (len(dirlist) == 0):
                    try:
                        os.rmdir(root)
                        logger.info("Removed: %s", root)
                        results['dirsRemoved'] += 1
                        if (detailedResults):
                            results['dirsRemovedList'].append(relRoot)
                    except (IOError, OSError):
                        logger.info("Remove failed: %s", relRoot)
                        results['dirsFailed'] += 1
                        if (detailedResults):
                            results['dirsFailedList'].append(relRoot)
                else:
                    results['dirsFailed'] += 1
                    if (detailedResults):
                        results['dirsFailedList'].append(relRoot)

    # If detailedResults was not desired remove those entries from the results
    if (not detailedResults):
        results['filesCopiedList'] = None
        results['filesFailedList'] = None
        results['filesSkippedList'] = None
        results['dirsCopiedList'] = None
        results['dirsFailedList'] = None
        results['dirsSkippedList'] = None

    return results


'''
Moves all files and folders from the given source directory to the destination.

:type src:string
:param src: The source path to move from

:type dst:string
:param dst: The destination path to move to

:type includeFiles:array
:param includeFiles: A list of regex and wildcard patterns of files to include during the operation.
                     Files not matching at least one pattern in the include list will be skipped.
                     Regex patterns must be prefixed with re:

:type includeDirs:array
:param includeDirs: A list of regex and wildcard patterns of directory names to include during the operation.
                    Directories not matching at least one pattern in the include list will be skipped.
                    Regex patterns must be prefixed with re:

:type excludeFiles:array
:param excludeFiles: A list of regex and wildcard patterns of files to exclude during the operation.
                     Regex patterns must be prefixed with re:

:type excludeDirs:array
:param excludeDirs: A list of regex and wildcard patterns of directory names to exclude during the operation.
                    Regex patterns must be prefixed with re:

:type level:int
:param level: The maximum depth to traverse in the source directory tree.
               A value of 0 traverses the entire tree.
               A positive value traverses N levels from the top with value 1 being the source root.
               A negative value traverses N levels from the bottom of the source tree.

:type followLinks:bool
:param followLinks: Set to true to traverse through symbolic links.

:type forceOverwrite:bool
:param forceOverwrite: Set to true to overwrite destination files even if they are newer.

:type preserveStats:bool
:param preserveStats: Set to True to copy the source file stats to the destination.

:type detailedResults:bool
:param detailedResults: Set to True to include additional details in the results containing a list of all files and
                        directories that were skipped or failed during the operation.

:rtype:dict
:return: Returns a dictionary containing the following stats:
         'filesMoved', 'filesFailed', 'filesSkipped', 'dirsMoved', 'dirsFailed', 'dirsSkipped'
         If detailedResults is set to True also includes the following:
         'filesMovedList':list, 'filesFailedList':list, 'filesSkippedList':list,
         'dirsMovedList':list, 'dirsFailedList':list, 'dirsSkippedList':list
'''


def move(src, dst, includeFiles=None, includeDirs=None, excludeFiles=None, excludeDirs=None, level=0,
         followLinks=False, forceOverwrite=False, preserveStats=True, detailedResults=False):
    # Always work with absolute paths
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)

    # Attempt to copy everything
    copyResults = copy(src, dst, includeFiles=includeFiles, includeDirs=includeDirs, excludeFiles=excludeFiles,
                       excludeDirs=excludeDirs, level=level, followLinks=followLinks, forceOverwrite=forceOverwrite,
                       preserveStats=preserveStats, detailedResults=True)

    # Delete the source tree. Don't remove anything that was in the list of failed or skipped files/dirs
    for root, dirs, files in os.walk(src, topdown=False):
        relRoot = os.path.relpath(root, src)

        deleteDir = True
        # Was this directory skipped or failed?
        for failedDir in copyResults['dirsFailedList']:
            if (relRoot.lower() == failedDir.lower()):
                deleteDir = False
                break
        for skippedDir in copyResults['dirsSkippedList']:
            if (relRoot.lower() == skippedDir.lower()):
                deleteDir = False
                break

        if (deleteDir):
            # Attempt to delete all files in directory
            for file in files:
                filePath = os.path.join(root, file)
                relFilePath = os.path.join(relRoot, file)
                if (not os.path.lexists(filePath)):
                    continue

                deleteFile = True
                # Was the file skipped or failed?
                for failedFile in copyResults['filesFailedList']:
                    if (relFilePath.lower() == failedFile.lower()):
                        deleteFile = False
                        break
                for skippedFile in copyResults['filesSkippedList']:
                    if (relFilePath.lower() == skippedFile.lower()):
                        deleteFile = False
                        break

                if (deleteFile):
                    try:
                        os.remove(filePath)
                    except (IOError, OSError):
                        copyResults['filesFailedList'].append(relFilePath)

            # If all files were deleted it is safe to delete the directory
            dirlist = os.listdir(root)
            if (len(dirlist) == 0):
                if (os.path.islink(root)):
                    os.unlink(root)
                else:
                    try:
                        os.rmdir(root)
                    except (IOError, OSError):
                        copyResults['dirsFailed'].append(root)

    # Transpose results and return
    results = {}
    results['filesMoved'] = copyResults['filesCopied']
    results['filesFailed'] = copyResults['filesFailed']
    results['filesSkipped'] = copyResults['filesSkipped']
    results['dirsMoved'] = copyResults['dirsCopied']
    results['dirsFailed'] = copyResults['dirsFailed']
    results['dirsSkipped'] = copyResults['dirsSkipped']
    if (detailedResults):
        results['filesMovedList'] = copyResults['filesCopiedList']
        results['filesFailedList'] = copyResults['filesFailedList']
        results['filesSkippedList'] = copyResults['filesSkippedList']
        results['dirsMovedList'] = copyResults['dirsCopiedList']
        results['dirsFailedList'] = copyResults['dirsFailedList']
        results['dirsSkippedList'] = copyResults['dirsSkippedList']

    return results


'''
Synchronizes all files and folders between the two given paths.

This is equivalent to making the following calls:
copy(path1, path2)
copy(path2, path1)

:type path1:string
:param path1: The first path to synchronize

:type path2:string
:param path2: The second path to synchronize

:type includeFiles:array
:param includeFiles: A list of regex and wildcard patterns of files to include during the operation.
                     Files not matching at least one pattern in the include list will be skipped.
                     Regex patterns must be prefixed with re:

:type includeDirs:array
:param includeDirs: A list of regex and wildcard patterns of directory names to include during the operation.
                    Directories not matching at least one pattern in the include list will be skipped.
                    Regex patterns must be prefixed with re:

:type excludeFiles:array
:param excludeFiles: A list of regex and wildcard patterns of files to exclude during the operation.
                     Regex patterns must be prefixed with re:

:type excludeDirs:array
:param excludeDirs: A list of regex and wildcard patterns of directory names to exclude during the operation.
                    Regex patterns must be prefixed with re:

:type level:int
:param level: The maximum depth to traverse in the source directory tree.
               A value of 0 traverses the entire tree.
               A positive value traverses N levels from the top with value 1 being the source root.
               A negative value traverses N levels from the bottom of the source tree.

:type followLinks:bool
:param followLinks: Set to true to traverse through symbolic links.

:type forceOverwrite:bool
:param forceOverwrite: Set to true to overwrite destination files even if they are newer.

:type preserveStats:bool
:param preserveStats: Set to True to copy the source file stats to the destination.

:type detailedResults:bool
:param detailedResults: Set to True to include additional details in the results containing a list of all files and
                        directories that were skipped or failed during the operation.

:rtype:dict
:return: Returns a dictionary containing the following stats:
         'filesCopied':int, 'filesFailed':int, 'filesSkipped':int, 'dirsCopied':int, 'dirsFailed':int, 'dirsSkipped':int
         If detailedResults is set to True also includes the following:
         'filesFailedList':list, 'filesSkippedList':list, 'dirsFailedList':list, 'dirsSkippedList':list
'''


def sync(path1, path2, includeFiles=None, includeDirs=None, excludeFiles=None, excludeDirs=None, level=0,
         followLinks=False, forceOverwrite=False, preserveStats=True, detailedResults=False):
    # Always work with absolute paths
    path1 = os.path.abspath(path1)
    path2 = os.path.abspath(path2)

    results = copy(path1, path2, includeFiles=includeFiles, includeDirs=includeDirs, excludeFiles=excludeDirs,
                   level=level, followLinks=followLinks, forceOverwrite=forceOverwrite, preserveStats=preserveStats,
                   detailedResults=True)
    results2 = copy(path2, path1, includeFiles=includeFiles, includeDirs=includeDirs, excludeFiles=excludeDirs,
                    level=level, followLinks=followLinks, forceOverwrite=forceOverwrite, preserveStats=preserveStats,
                    detailedResults=True)

    # Add new entries from results2 to the various lists of results
    for dpath in results2['filesCopiedList']:
        addPath = True
        for spath in results['filesCopiedList']:
            if (spath == dpath):
                addPath = False
                break
        if (addPath):
            results['filesCopiedList'].append(dpath)
    for dpath in results2['filesFailedList']:
        addPath = True
        for spath in results['filesFailedList']:
            if (spath == dpath):
                addPath = False
                break
        if (addPath):
            results['filesFailedList'].append(dpath)
    for dpath in results2['filesSkippedList']:
        addPath = True
        for spath in results['filesSkippedList']:
            if (spath == dpath):
                addPath = False
                break
        if (addPath):
            results['filesSkippedList'].append(dpath)
    for dpath in results2['dirsCopiedList']:
        addPath = True
        for spath in results['dirsCopiedList']:
            if (spath == dpath):
                addPath = False
                break
        if (addPath):
            results['dirsCopiedList'].append(dpath)
    for dpath in results2['dirsFailedList']:
        addPath = True
        for spath in results['dirsFailedList']:
            if (spath == dpath):
                addPath = False
                break
        if (addPath):
            results['dirsFailedList'].append(dpath)
    for dpath in results2['dirsSkippedList']:
        addPath = True
        for spath in results['dirsSkippedList']:
            if (spath == dpath):
                addPath = False
                break
        if (addPath):
            results['dirsSkippedList'].append(dpath)

    # Update the stats
    results['filesCopied'] = len(results['filesCopiedList'])
    results['filesFailed'] = len(results['filesFailedList'])
    results['filesSkipped'] = len(results['filesSkippedList'])
    results['dirsCopied'] = len(results['dirsCopiedList'])
    results['dirsFailed'] = len(results['dirsFailedList'])
    results['dirsSkipped'] = len(results['dirsSkippedList'])

    # If detailedResults was not desired remove those entries from the results
    if (not detailedResults):
        results['filesCopiedList'] = None
        results['filesFailedList'] = None
        results['filesSkippedList'] = None
        results['dirsCopiedList'] = None
        results['dirsFailedList'] = None
        results['dirsSkippedList'] = None

    return results


'''
Checks if the two given paths point to the same place.

:type src:string
:param src: The source path to check.

:type dst:string
:param dst: The destination path to check.

:rtype:bool
:return: Returns True if src and dst point to the same location, otherwise False.
'''


def _isSamePath(src, dst):
    # Mac/Unix
    if (hasattr(os.path, 'samefile')):
        try:
            return os.path.samefile(src, dst)
        except OSError:
            return False

    # All other platforms
    return (os.path.normcase(os.path.abspath(src)) ==
            os.path.normcase(os.path.abspath(dst)))


'''
Normalizes the given pattern by adding wildcards when path has more levels.

Note that on Windows regular expression patterns have issues with when using the path separator '\' character.
This function will switch all path separators in a regex pattern to use '/' instead.

e.g.
Given a path 'Level1' and pattern '*/Level2' would return '*/Level2'
Given a path 'Level1/Level2/Level3' and a pattern 'Level1' would return 'Level1/*/*'

:type path:string or regex
:param path: The pattern to normalize

:type path:string
:param path: The path to normalize the pattern for

:rtype:string or regex
:return: A string or regex object of the normalized pattern for the given path
'''


def _normalizeDirPattern(pattern, path):
    bIsRegex = False
    tmpPattern = pattern
    if (isinstance(pattern, re._pattern_type)):
        tmpPattern = pattern.pattern
        bIsRegex = True
    elif (pattern.startswith('re:')):
        tmpPattern = pattern[3:]
        bIsRegex = True

    numPathSep = path.count(os.path.sep)
    numPatternSep = tmpPattern.count(os.path.sep)

    # When the path has more levels, fill in the pattern with wildcards
    if (numPathSep > numPatternSep):
        while (numPathSep > numPatternSep):
            if (bIsRegex):
                if (tmpPattern != ''):
                    tmpPattern = tmpPattern + "/.*"
                else:
                    tmpPattern = '.*'
            else:
                tmpPattern = os.path.join(tmpPattern, "*")
            numPatternSep = numPatternSep + 1

    if (bIsRegex):
        return re.compile(tmpPattern)
    else:
        return tmpPattern


'''
Normalizes the given pattern by adding wildcards when path has more levels.

For patterns that are already multi-level wildcards are added to the middle of the path, before the tail, as
it is assumed the tail of the pattern is for filename matching and not just a path.

Note that on Windows regular expression patterns have issues with when using the path separator '\' character.
This function will switch all path separators in a regex pattern to use '/' instead.

e.g.
Given a filepath 'MyFile.txt' and a pattern '*.txt' will return '*.txt'
Given a filepath 'Level1/MyFile.txt' and a pattern '*.txt' will return '*/*.txt'
Given a filepath 'MyFile.txt' and a pattern 'Level1/*.txt' will return 'Level1/*.txt'
Given a filepath 'Level1/Level2/MyFile.txt' and a pattern 'Level1/*.txt' will return 'Level1/*/*.txt'

:type path:string or regex
:param path: The pattern to normalize

:type path:string
:param path: The path to normalize the pattern for

:rtype:string or regex
:return: A string or regex object of the normalized pattern for the given path
'''


def _normalizeFilePattern(pattern, filepath):
    bIsRegex = False
    tmpPattern = pattern
    if (isinstance(pattern, re._pattern_type)):
        tmpPattern = pattern.pattern
        bIsRegex = True
    elif (pattern.startswith('re:')):
        tmpPattern = pattern[3:]
        bIsRegex = True

    # Separate the file pattern from the dir/path pattern
    patternParts = os.path.split(tmpPattern)
    tmpPattern = patternParts[0]

    numPathSep = filepath.count(os.path.sep)
    numPatternSep = tmpPattern.count(os.path.sep)
    if (tmpPattern != ''):
        numPatternSep = numPatternSep + 1

    # When the path has more levels, fill in the pattern with wildcards
    if (numPathSep > numPatternSep):
        while (numPathSep > numPatternSep):
            if (bIsRegex):
                if (tmpPattern != ''):
                    tmpPattern = tmpPattern + "/.*"
                else:
                    tmpPattern = '.*'
            else:
                tmpPattern = os.path.join(tmpPattern, "*")
            numPatternSep = numPatternSep + 1

    # Append the file pattern back
    if (bIsRegex):
        tmpPattern = tmpPattern + "/" + patternParts[1]
    else:
        tmpPattern = os.path.join(tmpPattern, patternParts[1])

    if (bIsRegex):
        return re.compile(tmpPattern)
    else:
        return tmpPattern


'''
Determines if the given path will be copied given the list of includes and excludes.
When include patterns are provided the path must match at least one of the patterns
given and cannot be excluded

:type path:string
:param path: The path of the directory to check

:type bIsFile:bool
:param bIsFile: Set to true if path is for a file

:type includes:array
:param includes: The list of compiled inclusive regex patterns to check the path against

:type excludes:array
:param excludes: The list of compiled exclusive regex patterns to check the path against
'''


def _checkShouldCopy(path, bIsFile, includes, excludes):
    # The pattern will have '/' path separators (even on Windows). Make sure the path does too.
    rePath = path
    if (os.path.sep == '\\'):
        rePath = path.replace(os.path.sep, '/')

    # Now check the path against the include list.
    if (includes != None and len(includes) > 0):
        isIncluded = False
        for pattern in includes:
            normPattern = None
            if (bIsFile):
                normPattern = _normalizeFilePattern(pattern, path)
            else:
                normPattern = _normalizeDirPattern(pattern, path)

            if (isinstance(normPattern, re._pattern_type)):
                if (normPattern.match(rePath) != None):
                    isIncluded = True
                    break
            else:
                if (fnmatch.fnmatch(path, normPattern)):
                    isIncluded = True
                    break
        return isIncluded

    # Now check the exclude lists
    if (excludes != None):
        for pattern in excludes:
            normPattern = None
            if (bIsFile):
                normPattern = _normalizeFilePattern(pattern, path)
            else:
                normPattern = _normalizeDirPattern(pattern, path)

            if (isinstance(normPattern, re._pattern_type)):
                if (normPattern.match(rePath) != None):
                    return False
            else:
                if (fnmatch.fnmatch(path, normPattern)):
                    return False

    return True


'''
Copies a file from the give source path to the destination.

:type src:string
:param src: The path of the source file to copy.

:type dst:string
:param dst: The path of the destination to copy src to.

:type includes:array
:param includes: The list of compiled inclusive regex patterns to check the source path against.

:type excludes:array
:param excludes: The list of compiled exclusive regex patterns to check the source path against.

:type showProgress:bool
:param showProgress: Set to True to display real-time progress information about the operation. Progress is only shown
                     to stdout and stderr.

:type forceOverwrite:bool
:param forceOverwrite: Set to True to overwrite destination files even if they are newer.

:type preserveStats:bool
:param preserveStats: Set to True to copy the source file stats to the destination.

:rtype:int
:return: Returns a value 1 if the file was copied, value 0 if the file was skipped and -1 if an error occurred.
'''


def _copyFile(src, dst, includes=None, excludes=None, showProgress=True, forceOverwrite=False, preserveStats=True):
    # Only copy files
    if (not os.path.isfile(src)):
        return -1

    # Don't copy files to the same location
    if (_isSamePath(src, dst)):
        return -1

    # Should the file be copied?
    if (not _checkShouldCopy(src, True, includes, excludes)):
        return 0

    # Don't overwrite older copies of files unless explicitly desired
    if (not forceOverwrite and os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src)):
        return 0

    # Make sure the directory at the destination exists
    dstRoot = os.path.split(dst)[0]
    if (not os.path.isdir(dstRoot)):
        mkdir(dstRoot)

    # Finally perform the copy
    logger.info("Copying: %s => %s", src, dst)
    if (os.path.islink(src)):
        try:
            os.symlink(os.readlink(src), dst)
        except (IOError, OSError):
            return -1
    else:
        # The number of bytes per read operation
        global BUFFERSIZE_KIB
        maxReadLength = BUFFERSIZE_KIB * 1024
        try:
            with open(src, 'rb') as fsrc:
                with open(dst, 'wb') as fdst:
                    bytesTotal = os.path.getsize(src)
                    bytesWritten = 0
                    while 1:
                        buf = fsrc.read(maxReadLength)
                        if not buf:
                            break
                        fdst.write(buf)

                        bytesWritten += len(buf)
                        _displayProgress(bytesWritten, bytesTotal)
        except (IOError, OSError):
            return -1

        # Spit out an empty line so subsequent text starts on the next line
        logger.info("")

        # Copy file stats
        if (preserveStats):
            _copyStats(src, dst)

    # Was the copy successful?
    if (os.path.exists(dst)):
        # If the file isn't a symlink, check the size
        if (os.path.islink(dst) or os.path.getsize(src) == os.path.getsize(dst)):
            return 1

    return -1


'''
Copies the stat info (mode bits, atime, mtime, flags) from src to dst.

:type src:string
:param src: The source path to copy stat info from.

:type dst:string
:param dst: The destination path to copy stat info to.
'''


def _copyStats(src, dst):
    st = os.stat(src)
    mode = stat.S_IMODE(st.st_mode)
    if hasattr(os, 'utime'):
        os.utime(dst, (st.st_atime, st.st_mtime))
    if hasattr(os, 'chmod'):
        os.chmod(dst, mode)
    if hasattr(os, 'chflags') and hasattr(st, 'st_flags'):
        try:
            os.chflags(dst, st.st_flags)
        except OSError as why:
            for err in 'EOPNOTSUPP', 'ENOTSUP':
                if hasattr(errno, err) and why.errno == getattr(errno, err):
                    break
            else:
                raise


'''
Prints the current progress for the given file operation to any stdout or stderr handler attached to logger using the
INFO level.

:type currentValue:int
:param currentValue: The value representing the current progress.

:type totalValue:int
:param totalValue: The maximum value of the progress to be achieved.
'''


def _displayProgress(currentValue, totalValue):
    # Displaying the progress bar should only be shown at the appropriate log level (INFO)
    if (logger.getEffectiveLevel() > logging.INFO):
        return

    # Attempt to grab all available stdout/stderr streams from the list of logger handlers
    streams = []
    for handler in logger.handlers:
        if (isinstance(handler, logging.StreamHandler) and
                (handler.stream is sys.stderr or handler.stream is sys.stdout)):
            streams.append(handler.stream)

    # If no output streams were found we can't display the progress bar
    if (len(streams) == 0):
        return

    strToDisplay = str(currentValue) + " / " + str(totalValue) + " ["

    # Add the progress bar
    maxLineLength = 80
    percentComplete = float(currentValue) / float(totalValue)
    currentBarValue = int(maxLineLength * percentComplete)
    i = 0
    while (i < maxLineLength):
        if (i < currentBarValue):
            strToDisplay += "="
        elif (i == currentBarValue):
            strToDisplay += ">"
        else:
            strToDisplay += " "
        i += 1

    strToDisplay += "]\r"

    for stream in streams:
        stream.write(strToDisplay)
        stream.flush()


'''
Prints a table showing the results of a copy operation to the INFO log.

:type results:dict
:param results: The dictionary containing the copy results to display.
'''


def _displayCopyResults(results):
    if (logger.getEffectiveLevel() > logging.ERROR):
        return

    logger.info("--------------------")
    logger.info("Files:")
    if ('filesCopied' in results):
        logger.info("\tCopied: %d", results['filesCopied'])
    if ('filesMoved' in results):
        logger.info("\tMoved: %d", results['filesMoved'])
    if ('filesRemoved' in results):
        logger.info("\tRemoved: %d", results['filesRemoved'])
    logger.info("\tSkipped: %d", results['filesSkipped'])
    logger.info("\tFailed: %d", results['filesFailed'])
    logger.info("")
    logger.info("Directories:")
    if ('dirsCopied' in results):
        logger.info("\tCopied: %d", results['dirsCopied'])
    if ('dirsMoved' in results):
        logger.info("\tMoved: %d", results['dirsMoved'])
    if ('dirsRemoved' in results):
        logger.info("\tRemoved: %d", results['dirsRemoved'])
    logger.info("\tSkipped: %d", results['dirsSkipped'])
    logger.info("\tFailed: %d", results['dirsFailed'])
    logger.info("--------------------")


'''
Determines the maximum depth of the tree for a given path.

:type path:string
:param path: The path to compute the depth for.

:rtype:int
:return: The maximum depth of path.
'''


def _getTreeDepth(path):
    maxDepth = 0
    for root, dirs, files in os.walk(path):
        relRoot = os.path.relpath(root, path)
        depth = relRoot.count(os.path.sep) + 1
        if (depth > maxDepth):
            maxDepth = depth
    return maxDepth
