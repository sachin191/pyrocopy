import argparse
import logging
# from . import pyrocopy
import pyrocopy

def main():
    parser = argparse.ArgumentParser(description='A robust file copying utility.')

    copymode_group = parser.add_argument_group('copy mode')
    parser.add_argument("source", type=str, help="The path to copy contents from")
    parser.add_argument("destination", type=str, help="The path to copy contents to")

    mode_group = copymode_group.add_mutually_exclusive_group()
    mode_group.add_argument("--mirror", action='store_true', required=False, help="Creates an exact copy of source to the destination removing any files or directories in destination not also contained in source.")
    mode_group.add_argument("--move", action='store_true', required=False, help="Moves all files and directories from source to destination (delete from source after copying).")
    mode_group.add_argument("--sync", action='store_true', required=False, help="Performs a bi-directional copy of the contents of source and destination to contain the exact same set of files and directories in both locations.")

    copy_group = parser.add_argument_group('copy options')
    copy_group.add_argument("-f", "--force", action='store_true', required=False, help="Overwrites all files in destination from source even if newer.")
    copy_group.add_argument("--nostat", action='store_true', required=False, help="Do not copy file stats (mode bits, atime, mtime, flags)")
    
    select_group = parser.add_argument_group('selection options')
    select_group.add_argument("-if", "--includefiles", action='append', type=str, required=False, help="A list of regular expression or wildcard patterns for file inclusions. Regex patterns must include the prefix: re:")
    select_group.add_argument("-id", "--includedirs", action='append', type=str, required=False, help="A list of regular expression or wildcard patterns for directory inclusions. Regex patterns must include the prefix: re:")
    select_group.add_argument("-xf", "--excludefiles", action='append', type=str, required=False, help="A list of regular expression or wildcard patterns for file exclusions. Regex patterns must include the prefix: re:")
    select_group.add_argument("-xd", "--excludedirs", action='append', type=str, required=False, help="A list of regular expression or wildcard patterns for directory exclusions. Regex patterns must include the prefix: re:")
    select_group.add_argument("-l", "--level", type=int, default=0, required=False, help="The maximum depth level to traverse during the copy, starting from the source root. A negative value starts from the furthest node from the source root.")
    select_group.add_argument("-fl", "--followlinks", action='store_true', required=False, help="Traverses symbolic links as directories instead of copying the link.")
    
    log_group = parser.add_argument_group('logging options')
    log_exc_group = log_group.add_mutually_exclusive_group()
    log_exc_group.add_argument("-q", "--quiet", action='count', default=0, required=False, help="Shows less output during the operation.")
    log_exc_group.add_argument("-v", "--verbose", action='count', default=0, required=False, help="Shows more output during the operation.")

    parser.add_argument("--version", action='version', version="pyrocopy " + pyrocopy.__version_str__)

    args = parser.parse_args()

    # Set up logger
    pyrocopy.logger.addHandler(logging.StreamHandler())

    # Default log level is INFO. Change the level up/down depending on the option chosen.
    pyrocopy.logger.setLevel(logging.INFO)
    if (args.quiet > 0):
        pyrocopy.logger.setLevel(logging.INFO + (args.quiet * 10))
    elif (args.verbose > 0):
        pyrocopy.logger.setLevel(logging.INFO - (args.verbose * 10))

    # Perform the desired operation
    results = None
    if (args.mirror):
        results = pyrocopy.mirror(args.source, args.destination, includeFiles=args.includefiles, includeDirs=args.includedirs, excludeFiles=args.excludefiles, excludeDirs=args.excludedirs, level=args.level, followLinks=args.followlinks, forceOverwrite=args.force, preserveStats=(not args.nostat))
    elif (args.move):
        results = pyrocopy.move(args.source, args.destination, includeFiles=args.includefiles, includeDirs=args.includedirs, excludeFiles=args.excludefiles, excludeDirs=args.excludedirs, level=args.level, followLinks=args.followlinks, forceOverwrite=args.force, preserveStats=(not args.nostat))
    elif (args.sync):
        results = pyrocopy.sync(args.source, args.destination, includeFiles=args.includefiles, includeDirs=args.includedirs, excludeFiles=args.excludefiles, excludeDirs=args.excludedirs, level=args.level, followLinks=args.followlinks, forceOverwrite=args.force, preserveStats=(not args.nostat))
    else:
        results = pyrocopy.copy(args.source, args.destination, includeFiles=args.includefiles, includeDirs=args.includedirs, excludeFiles=args.excludefiles, excludeDirs=args.excludedirs, level=args.level, followLinks=args.followlinks, forceOverwrite=args.force, preserveStats=(not args.nostat))

    pyrocopy._displayCopyResults(results)

# main program
main()
