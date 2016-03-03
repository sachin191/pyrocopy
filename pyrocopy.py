'''
Copyright 2016 Jean-Philippe Steinmetz
'''

import logging
import os
import re
import shutil

# Set up a logger
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())

'''
Determines if the given path should be copied given the list of includes and excludes.

:type path:string
:param path: The path to check

:type includes:array
:param includes: The list of compiled regex patterns to check the path against

:type excludes:array
:param excludes: The list of compiled regex patterns to check the path against
'''
def shouldCopy(path, includes, excludes):
    # Check the file against the include list
    isIncluded = False
    for pattern in includes:
        if (re.match(pattern, path) != None):
            isIncluded = True
            break

    # Now check the exclude list
    isExcluded = False
    if (isIncluded == False):
        for pattern in excludes:
            if (re.match(pattern, path) != None):
                isExcluded = True
                break

    # An explicit include always overrides the exclude
    return isIncluded or isExcluded == False

'''
Copies all files from the given source directory to the destination.

:type srcPath:string
:param srcPath: The source path to copy from

:type dstPath:string
:param dstPath: The destination path to copy to

:type include:array
:param include: A list of regex patterns of files to include during the operation.
                Files matching the include list always get copied, even if there is a match in the exclude list.

:type exclude:array
:param exclude: A list of regex patterns of files to exclude during the operation.
                Files matching the exclude list can be overriden by the include list.

:type level:int
:param level: The maximum depth to traverse in the source directory tree.
               A value of 0 traverses the entire tree.
               A positive value traverses N levels from the top with value 1 being the source root.
               A negative value traverses N levels from the bottom of the source tree.

:type followLinks:bool
:param followLinks: Set to true to traverse through symbolic links.

:type loglevel:int
:param loglevel: The logging level to use for output. See module logging for values.
'''
def copy(srcPath, dstPath, includes=None, excludes=None, level=0, followLinks=False, loglevel=logging.INFO):
    # Set the logger level
    logger.setLevel(loglevel)

    # Stats
    numCopied = 0
    numFailed = 0
    numSkipped = 0
    numDirSkipped = 0
    
    # Compile the provided regex patterns
    includePatterns = []
    if (includes != None):
        for pattern in includes:
            includePatterns.append(re.compile(pattern))
    excludePatterns = []
    if (excludes != None):
        for pattern in excludes:
            excludePatterns.append(re.compile(pattern))

    # Is the source path a file or directory?
    if (os.path.isfile(srcPath)):
        # Is the destination path a file name or directory?
        if (os.path.isdir(dstPath)):
            dstPath = os.path.join(dstPath, os.path.basename(srcPath))

        # Should the file be copied?
        if (shouldCopy(srcPath, includePatterns, excludePatterns) == False):
            logger.info("Skipped: %s", srcPath)
            numSkipped += 1
        elif (os.path.exists(dstPath) and os.path.getmtime(dstPath) >= os.path.getmtime(srcPath)):
            logger.info("Skipped: %s", srcPath)
            numSkipped += 1
        else:
            shutil.copy2(srcPath, dstPath)
            if (os.path.exists(dstPath)):
                logger.info("Copied: %s => %s", srcPath, dstPath)
                numCopied += 1
            else:
                logger.info("Failed: %s => %s", srcPath, dstPath)
                numFailed += 1
    else:
        # Make sure the destination exists to copy files to
        if (os.path.isdir(dstPath) == False):
            os.mkdir(dstPath)

        for root, dirs, files in os.walk(srcPath, followlinks=followLinks):
            relRoot = os.path.relpath(root, srcPath)

            # Is the root a symlink? Should we follow?
            if (os.path.islink(root) and followLinks == False):
                logger.info("Skipped: %s", root)
                numDirSkipped += 1
                continue

            # Exclude items not at the desired depth
            if (level != 0):
                depth = relRoot.count(os.path.sep) + 1
                if (depth >= abs(level)):
                    logger.info("Skipped: %s", relRoot)
                    numDirSkipped += 1
                    continue

            # Should the directory be traversed?
            if (shouldCopy(relRoot, includePatterns, excludePatterns) == False):
                logger.info("Skipped: %s", relRoot)
                numDirSkipped += 1
                continue

            # Make sure the root directory exists at the destination
            dstRoot = os.path.join(dstPath, relRoot)
            if (os.path.isdir(dstRoot) == False):
                os.mkdir(dstRoot)
        
            for file in files:
                filePath = os.path.join(relRoot, file)

                # Should the file be copied?
                if (shouldCopy(filePath, includePatterns, excludePatterns) == False):
                    logger.info("Skipping: %s", filePath)
                    numSkipped += 1
                    continue

                # Don't overwrite older copies of files unless explicitly desired
                srcFilePath = os.path.join(srcPath, root, file)
                dstFilePath = os.path.join(dstPath, filePath)
                if (os.path.exists(dstFilePath) and os.path.getmtime(dstFilePath) >= os.path.getmtime(srcFilePath)):
                    logger.info("Skipping: %s", filePath)
                    numSkipped += 1
                    continue

                # Make sure the parent directory exists
                dstRoot = os.path.join(dstPath, relRoot)
                if (os.path.isdir(dstRoot) == False):
                    os.mkdir(dstRoot)

                # Finally, copy the file
                shutil.copy2(srcFilePath, dstFilePath)
                if (os.path.exists(dstFilePath)):
                    logger.info("Copied: %s => %s", filePath, dstFilePath)
                    numCopied += 1
                else:
                    logger.info("Failed: %s => %s", filePath, dstFilePath)
                    numFailed += 1

    logger.info("")
    logger.info("--------------------")
    logger.info("Operation Completed:")
    logger.info("--------------------")
    logger.info("Copied:  %d", numCopied)
    logger.info("Failed:  %d", numFailed)
    logger.info("Skipped: Files: %d, Directories: %d", numSkipped, numDirSkipped)
    logger.info("--------------------")
