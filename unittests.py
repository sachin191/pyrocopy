'''
Copyright (C) 2016 Jean-Philippe Steinmetz
'''

import logging
import os
import pyrocopy
import random
import shutil
import tempfile

# Set up the logger
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

'''
Generate a random directory tree.

:type path:string
:param path: The initial path to create the tree in.

:type maxLevels:int
:param maxLevels: The maximum depth of the tree to create.

:type totalFiles:int
:param totalFiles: The maximum number of files to create in the tree.

:type maxFileSize:int
:param maxFileSize: The maximum file size that can be created.

:rtype:string
:return: The path of the newly generated directory tree.
'''
def genRandomTree(path, maxlevels, totalFiles, maxFileSize):
    logger.info("Generating random directory tree...")
    
    # Generate a random name for the tree root
    root = os.path.join(path, "d" + str(random.randint(0, totalFiles * totalFiles)))
    logger.info("Path: %s", root)

    os.mkdir(root)

    numFiles = 0
    while (numFiles < totalFiles):
        depth = random.randint(0, maxlevels)

        # Randomly generate the current directory to create files in
        curDir = root
        i = 0
        while (i < depth):
            tmp = os.path.join(curDir, "d" + str(random.randint(0, totalFiles * totalFiles)))
            if (not os.path.exists(tmp)):
                os.mkdir(tmp)
            curDir = tmp
            i += 1

        # Randomly create a number of new files
        maxToCreate = totalFiles - numFiles
        numToCreate = random.randint(0, maxToCreate)
        curFile = 0
        while (curFile < numToCreate):
            filename = "f" + str(random.randint(0, totalFiles * totalFiles))
            filepath = os.path.join(curDir, filename)
            logger.info("Creating: %s", filepath)
            with open(filepath, 'w') as file:
                # Randomly generate data in the file
                totalChars = random.randint(0, maxFileSize)
                curChar = 0
                while (curChar < totalChars):
                    file.write(chr(random.randint(1,255)))
                    curChar += 1
                    if (curChar % (maxFileSize / 100) == 0):
                        pyrocopy._displayProgress(curChar, totalChars)
                file.flush()
            curFile += 1

            logger.info("")

        numFiles += numToCreate

    return root

# Create a temporary place to work
logger.info("Creating temp directory...")
tmpdir = tempfile.mkdtemp()

try:
    # mkdir test
    logger.info("Testing pyrocopy.mkdir() ...")
    mkdirTestPath = os.path.join(tmpdir, "Level1", "Level2", "Level3", "Level4")
    if (not os.path.isdir(mkdirTestPath)):
        if (not pyrocopy.mkdir(mkdirTestPath)):
            raise Exception("Failed to create mkdirTestPath!")

        if (os.path.isdir(mkdirTestPath)):
            if (not pyrocopy.mkdir(mkdirTestPath)):
                raise Exception("Unexpected result: mkdirTestPath exists!")
        else:
            raise Exception("Failed to create mkdirTestPath!")
    else:
        raise Exception("mkdirTestPath already exists!")

    # copy test
    logger.info("Testing pyrocopy.copy() ...")
    numFiles = 30
    src = genRandomTree(tmpdir, 4, numFiles, 16 * 1024)
    #src = genRandomTree("C:\\", 4, numFiles, 16 * 1024)
    dst = os.path.join(tmpdir, os.path.basename(src) + "Copy")
    #dst = os.path.join("C:\\", os.path.basename(src) + "Copy")

    # check initial copy
    result = pyrocopy.copy(src, dst)
    if (result != numFiles):
        raise Exception("Failed to copy all files.")
    # TODO Diff src and dst

    # check second copy (should skip all files)
    result = pyrocopy.copy(src, dst)
    if (result != 0):
        raise Exception("Failed to skip all files.")
    # TODO Diff src and dst

    # check overwrite copy
    result = pyrocopy.copy(src, dst, forceOverwrite=True)
    if (result != numFiles):
        raise Exception("Failed to overwrite all files.")
    # TODO Diff src and dst

    logger.info("Tests complete!")

except Exception as err:
    # clean up temp
    logger.info("Deleting temp files...")
    shutil.rmtree(tmpdir)

    raise err