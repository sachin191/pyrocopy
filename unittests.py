'''
Copyright (C) 2016 Jean-Philippe Steinmetz
'''

import logging
import os
import pyrocopy
import random
import re
import shutil
import sys
import tempfile

# Set up the logger
logger = logging.getLogger()
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

'''
Writes random contents to the file at the specified path.

:type path:string
:param path: The path to the file to write.

:type maxFileSize:int
:param maxFileSize: The maximum size of the file contents to generate.
'''
def genRandomContents(path, maxFileSize):
    with open(path, 'w') as file:
        # Randomly generate data in the file
        totalChars = random.randint(0, maxFileSize)
        curChar = 0
        while (curChar < totalChars):
            file.write(chr(random.randint(1,255)))
            curChar += 1
            if (curChar % (maxFileSize / 100) == 0):
                pyrocopy._displayProgress(curChar, totalChars)
        file.flush()
        logger.info("")

'''
Creates a new file at the given path with random contents.

:type path:string
:param path: The path to a directory to create the new file in.

:type maxFileSize:int
:param maxFileSize: The maximum size of the file to create.

:rtype:string
:return: The path to the newly created file.
'''
def genRandomFile(path, maxFileSize):
    filename = "f" + str(random.randint(0, sys.maxint))
    filepath = os.path.join(path, filename)

    logger.info("Creating: %s", filepath)
    genRandomContents(filepath, maxFileSize)
    
    return filename

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
            genRandomFile(curDir, maxFileSize)
            curFile += 1

        numFiles += numToCreate

    return root

# Create a temporary place to work
logger.info("Creating temp directory...")
tmpdir = tempfile.mkdtemp()

# Constants
MAX_FILE_SIZE = 16 * 1024

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
    src = genRandomTree(tmpdir, 4, numFiles, MAX_FILE_SIZE)
    #src = genRandomTree("C:\\", 4, numFiles, MAX_FILE_SIZE)
    dst = os.path.join(tmpdir, os.path.basename(src) + "Copy")
    #dst = os.path.join("C:\\", os.path.basename(src) + "Copy")

    # check initial copy
    results = pyrocopy.copy(src, dst)
    if (results['filesCopied'] != numFiles):
        raise Exception("Failed to copy all files.")
    if (results['filesFailed'] > 0 or results['dirsFailed'] > 0):
        raise Exception("Failed to copy some files or directories.")
    # TODO Diff src and dst

    # check second copy (should skip all files)
    results = pyrocopy.copy(src, dst)
    if (results['filesSkipped'] != numFiles):
        raise Exception("Failed to skip all files.")
    if (results['filesFailed'] > 0 or results['dirsFailed'] > 0):
        raise Exception("Failed to process some files or directories.")
    # TODO Diff src and dst

    # check overwrite copy
    results = pyrocopy.copy(src, dst, forceOverwrite=True)
    if (results['filesCopied'] != numFiles):
        raise Exception("Failed to overwrite all files.")
    if (results['filesFailed'] > 0 or results['dirsFailed'] > 0):
        raise Exception("Failed to copy some files or directories.")
    # TODO Diff src and dst

    shutil.rmtree(dst)

    # check depth level copy
    src = genRandomTree(tmpdir, 0, 5, MAX_FILE_SIZE)
    lvl1 = genRandomTree(src, 0, 3, MAX_FILE_SIZE)
    lvl2 = genRandomTree(lvl1, 0, 7, MAX_FILE_SIZE)
    dst = os.path.join(tmpdir, os.path.basename(src) + "Copy")

    results = pyrocopy.copy(src, dst, level=1)
    if (results['filesCopied'] != 5):
        raise Exception("Failed to copy at depth level 1")

    shutil.rmtree(dst)
    results = pyrocopy.copy(src, dst, level=-1)
    if (results['filesCopied'] != 7):
        raise Exception("Failed to copy at depth level -1")

    shutil.rmtree(dst)
    results = pyrocopy.copy(src, dst, level=2)
    if (results['filesCopied'] != 8):
        raise Exception("Failed to copy at depth level 2")

    shutil.rmtree(dst)
    results = pyrocopy.copy(src, dst, level=-2)
    if (results['filesCopied'] != 10):
        raise Exception("Failed to copy at depth level -2")

    shutil.rmtree(dst)
    genRandomContents(os.path.join(src, "file1"), MAX_FILE_SIZE)
    genRandomContents(os.path.join(lvl1, "test"), MAX_FILE_SIZE)
    os.mkdir(os.path.join(src, "dummydir"))
    genRandomContents(os.path.join(src, "dummydir", "dummy1"), MAX_FILE_SIZE)
    genRandomContents(os.path.join(src, "dummydir", "dummy2"), MAX_FILE_SIZE)
    os.mkdir(os.path.join(lvl1, "moredir"))
    i = 0
    while (i < 5):
        genRandomContents(os.path.join(lvl1, "moredir", "more"+str(i)), MAX_FILE_SIZE)
        i += 1

    # check file includes copy
    includeFiles = ['f[0-9]+']
    results = pyrocopy.copy(src, dst, includeFiles=includeFiles)
    if (results['filesCopied'] != 15):
        raise Exception("Failed to copy with includeFiles['f[0-9+']")
    for root, dirs, files in os.walk(dst):
        for file in files:
            if (not re.match('f[0-9]+', file)):
                raise Exception("Failed to include only files with pattern: f[0-9]+")

    # check file excludes copy
    shutil.rmtree(dst)
    excludeFiles = ['f[0-9]+']
    results = pyrocopy.copy(src, dst, excludeFiles=excludeFiles)
    if (results['filesCopied'] != 9):
        raise Exception("Failed to copy with excludeFiles['f[0-9+']")
    for root, dirs, files in os.walk(dst):
        for file in files:
            if (re.match('f[0-9]+', file)):
                raise Exception("Failed to exclude files with pattern: f[0-9]+")

    # check dir includes copy
    shutil.rmtree(dst)
    includeDirs = ['d[0-9]+']
    results = pyrocopy.copy(src, dst, includeDirs=includeDirs)
    if (results['filesCopied'] != 17):
        raise Exception("Failed to copy with includeDirs=['d[0-9]+']")
    for root, dirs, files in os.walk(dst):
        for dir in dirs:
            if (dir == "moredir" or dir == "dummydir"):
                raise Exception("Failed to only include specified directories.")

    # check dir excludes copy
    shutil.rmtree(dst)
    excludeDirs = ['moredir']
    results = pyrocopy.copy(src, dst, excludeDirs=excludeDirs)
    if (results['filesCopied'] != 19):
        raise Exception("Failed to copy with excludeDirs=['moredir']")
    for root, dirs, files in os.walk(dst):
        for dir in dirs:
            if (dir == "moredir"):
                raise Exception("Failed to only exclude directory 'moredir'.")

    # check move
    shutil.rmtree(dst)
    dst = os.path.join(tmpdir, os.path.basename(src)+"Moved")

    results = pyrocopy.move(src, dst)
    if (results['filesMoved'] != 24):
        raise Exception("Failed to move all files")
    if (os.path.exists(src) and os.listdir(src).count > 0):
        raise Exception("Move did not delete source")

    # check move depth level
    results = pyrocopy.move(dst, src, level=1)
    if (results['filesMoved'] != 6):
        raise Exception("Failed to move at depth level 1.")
    if (not os.path.exists(dst)):
        raise Exception("Move with depth level 1 deleted whole tree!")
    
    results = pyrocopy.move(dst, src, level=-1)
    if (results['filesMoved'] != 12):
        raise Exception("Failed to move at depth level -1.")
    if (not os.path.exists(dst)):
        raise Exception("Move with depth level -1 deleted whole tree!")

    # Move the rest of the files
    results = pyrocopy.move(dst, src)
    if (results['filesMoved'] != 6):
        raise Exception("Failed to move remainder of files")
    if (os.path.exists(dst)):
        raise Exception("Move did not delete source")

    # check move dir includes
    includeDirs = ['dummydir']
    results = pyrocopy.move(src, dst, includeDirs=includeDirs)
    if (results['filesMoved'] != 8):
        raise Exception("Failed move with dir includes: 'dummydir'")

    # check move dir excludes
    excludeDirs = ['moredir']
    results = pyrocopy.move(src, dst, excludeDirs=excludeDirs)
    if (results['filesMoved'] != 9 and results['filesSkipped'] != 5):
        raise Exception("Failed to move with dir excludes: 'moredir'")

    # check move file includes
    includeFiles = ['f[0-9]+']
    results = pyrocopy.move(src, dst, includeFiles=includeFiles)
    if (results['filesMoved'] != 5 and results['filesSkipped'] != 2):
        raise Exception("Failed to move with file includes: 'f[0-9]+'")

    # check move file excludes
    excludeFiles = ['test']
    results = pyrocopy.move(src, dst, excludeFiles=excludeFiles)
    if (results['filesMoved'] != 1 and results['filesSkipped'] != 1):
        raise Exception("Failed to move with file excludes: test")

    logger.info("Tests complete!")

except Exception as err:
    # Store original trace
    (_, _, traceback) = sys.exc_info()
    
    # clean up temp
    logger.info("Deleting temp files...")
    shutil.rmtree(tmpdir)

    # Re-raise with original trace
    raise err, None, traceback