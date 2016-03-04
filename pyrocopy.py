'''
Robust file utilities for Python inspired by Windows' robocopy.

Copyright (C) 2016 Jean-Philippe Steinmetz
'''

import logging
import os
import re
import sys

'''
The logger used to report information and progress during operations.

The default log level is INFO.
'''
logger = logging.getLogger()
logger.addHandler(logging.NullHandler())

'''
Copies all files from the given source directory to the destination.

:type src:string
:param src: The source path to copy from

:type dst:string
:param dst: The destination path to copy to

:type includeFiles:array
:param includeFiles: A list of regex patterns of files to include during the operation.
                     Files not matching at least one pattern in the include list will be skipped.

:type includeDirs:array
:param includeDirs: A list of regex patterns of directory names to include during the operation.
                    Directories not matching at least one pattern in the include list will be skipped.

:type excludeFiles:array
:param excludeFiles: A list of regex patterns of files to exclude during the operation.

:type excludeDirs:array
:param excludeDirs: A list of regex patterns of directory names to exclude during the operation.

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

:rtype:int
:return: Upon success returns a positive value indicating the number of files copied (including zero). If a failure
        occurred returns the number of failed files as a negative value.
'''
def copy(src, dst, includeFiles=None, includeDirs=None, excludeFiles=None, excludeDirs=None, level=0,
         followLinks=False, forceOverwrite=False, preserveStats=True):
    result = 0

    # Stats
    numCopied = 0
    numFailed = 0
    numSkipped = 0
    numDirSkipped = 0
    
    # Compile the provided regex patterns
    includeFilePatterns = []
    if (includeFiles != None):
        for pattern in includeFiles:
            includeFilePatterns.append(re.compile(pattern))
    includeDirPatterns = []
    if (includeDirs != None):
        for pattern in includeDirs:
            includeDirPatterns.append(re.compile(pattern))
    excludeFilePatterns = []
    if (excludeFiles != None):
        for pattern in excludeFiles:
            excludeFilePatterns.append(re.compile(pattern))
    excludeDirPatterns = []
    if (excludeDirs != None):
        for pattern in excludeDirs:
            excludeDirPatterns.append(re.compile(pattern))

    if (not _isSamePath(src, dst)):
        # Is the source path a file, directory or symlink?
        if (os.path.isfile(src) or (not followLinks and os.path.islink(src))):
            # Is the destination path a file name or directory?
            if (os.path.isdir(dst)):
                dst = os.path.join(dst, os.path.basename(src))

            # Copy the file
            result = _copyFile(src, dst, includeFilePatterns, excludeFilePatterns)
            if (result == 1):
                logger.info("Copied: %s => %s", src, dst)
                numCopied += 1
            elif (result == 0):
                logger.info("Skipped: %s", src)
                numSkipped += 1
            else:
                logger.error("Failed: %s => %s", src, dst)
                numFailed += 1
        elif (os.path.isdir(src)):
            # Make sure the destination exists to copy files to
            if (not os.path.isdir(dst)):
                mkdir(dst)

            # Determine the max depth. We can do this easily by walking in reverse
            maxDepth = 0
            for root, dirs, files in os.walk(src, topdown=False, followlinks=followLinks):
                relRoot = os.path.relpath(root, src)
                maxDepth = relRoot.count(os.path.sep) + 1
                break
            
            # Traverse the tree and begin copying
            for root, dirs, files in os.walk(src, topdown=(level >= 0), followlinks=followLinks):
                relRoot = os.path.relpath(root, src)

                logger.debug("Processing Directory: %s", relRoot)

                # Is the root a symlink? Should we follow?
                if (os.path.islink(root) and not followLinks):
                    logger.info("Skipped: %s", root)
                    numDirSkipped += 1
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
                        numDirSkipped += 1
                        continue

                # Should the directory be traversed?
                if (relRoot != '.' and
                    not _checkShouldCopy(os.path.basename(relRoot), includeDirPatterns, excludeDirPatterns)):
                    logger.info("Skipped: %s", relRoot)
                    numDirSkipped += 1
                    continue

                # Make sure the root directory exists at the destination
                dstRoot = os.path.join(dst, relRoot)
                if (not os.path.isdir(dstRoot)):
                    if (not mkdir(dstRoot)):
                        logger.exception("Failed: %s", dstRoot)
                        numDirFailed += 1
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
                        numCopied += 1
                    elif (result == 0):
                        logger.info("Skipped: %s", filePath)
                        numSkipped += 1
                    else:
                        logger.error("Failed: %s => %s", filePath, dstFullPath)
                        numFailed += 1
        else:
            logger.error("Source path is not valid: %s", src)
            numFailed += 1
    else:
        logger.error("Cannot perform a copy to the same location.")
        numFailed += 1

    # The result should be the total number of files successfully copied. If no files were copied and there is at least
    # one failure then report a negative value for the number of failed copies.
    result = numCopied
    if (result == 0 and numFailed > 0):
        result = numFailed * -1

    # Report the results
    logger.info("")
    logger.info("--------------------")
    if (result >= 0):
        logger.info("Operation Completed:")
    else:
        logger.info("Operation Failed:")
    logger.info("--------------------")
    logger.info("Copied:  %d", numCopied)
    logger.info("Failed:  %d", numFailed)
    logger.info("Skipped: Files: %d, Directories: %d", numSkipped, numDirSkipped)
    logger.info("--------------------")

    return result

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
    if (not os.path.isdir(pair[0])):
        mkdir(pair[0])

    # Now does the parent directory exist?
    if (not os.path.isdir(pair[0])):
        return False

    # Attempt to create the directory
    os.mkdir(path)

    logger.debug("Created: %s", path)

    return os.path.isdir(path)

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
Determines if the given file name will be copied given the list of includes and excludes.
When include patterns are provided the filename must match at least one of the patterns
given and cannot be excluded

:type filename:string
:param filename: The name of the file to check

:type includes:array
:param includes: The list of compiled inclusive regex patterns to check the path against

:type excludes:array
:param excludes: The list of compiled exclusive regex patterns to check the path against
'''
def _checkShouldCopy(filename, includes, excludes):
    # Check the file against the include list
    if (len(includes) > 0):
        isIncluded = False
        for pattern in includes:
            if (re.match(pattern, filename) != None):
                isIncluded = True
                break
        return isIncluded

    # Now check the exclude lists
    for pattern in excludes:
        if (re.match(pattern, filename) != None):
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
        return 0

    # Don't copy files to the same location
    if (_isSamePath(src, dst)):
        return -1

    # Should the file be copied?
    if (not _checkShouldCopy(os.path.basename(src), includes, excludes)):
        return 0

    # Don't overwrite older copies of files unless explicitly desired
    if (not forceOverwrite and os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src)):
        return 0

    # Finally perform the copy
    logger.info("Copying: %s => %s", src, dst)
    if (os.path.islink(src)):
        os.symlink(os.readlink(src), dst)
    else:

        # The number of bytes per read operation
        maxReadLength = 16*1024
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
Copies the stat info from src to dst.

:type src:string
:param src: The source path to copy stat info from.

:type dst:string
:param dst: The destination path to copy stat info to.
'''
def _copyStats(src, dst):
    return
'''
Displays a progress for the given file operation.

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
