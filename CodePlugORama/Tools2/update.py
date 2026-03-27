#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Simple script to download the latest repeater list from WWARA.

Exit codes:
    0 success
    1 success, but nothing needs to be done
    2 user error
    3 system error
"""

# This really could have been a short shell script, but there's a small
# amount of security risk in running shell scripts from cron, or
# where they can be executed remotely over http.

import csv
import errno
import glob
import os
import re
import shutil
import signal
import sys
import zipfile

verbose = 0

def main():
    global verbose

    # Step 1: update the database

    try:
        os.mkdir("New")
    except OSError as e:
        pass  # already exists; let it go

    curl("https://www.wwara.org/DataBaseExtract.zip", "New/DataBaseExtract.zip")

    zfile = zipfile.ZipFile("New/DataBaseExtract.zip", 'r')
    zfile.extractall("New")
    zfile.close()

    filename = glob.glob("New/WWARA-rptrlist*.csv")
    if not filename:
        print("WWARA-rptrlist*.csv not found in archive", file=sys.stderr)
        return 3
    filename = filename[0]
    name = os.path.basename(filename)

    oldfiles = glob.glob("Sources/WWARA-rptrlist*.csv") # Delete these later

    try:
        os.rename(filename, os.path.join('Sources', name))
    except Exception as e:
        print(f"Failed to move {filename} into Sources: {e}", file=sys.stderr)
        return 3

    if oldfiles:
        try:
            for file in oldfiles:
                os.remove(file)
        except Exception as e:
            print(f"Failed to remove {file}: {e}", file=sys.stderr)

    return 0


import urllib.request

def curl(src, dst):
    with urllib.request.urlopen(src) as ifile, open(dst,'wb') as ofile:
        shutil.copyfileobj(ifile, ofile)


if __name__ == '__main__':
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    try:
        sys.exit(main())
    except KeyboardInterrupt as e:
        sys.exit(1)
    except Exception as e:
        print("Killed by exception", file=sys.stderr)
        raise
    finally:
        shutil.rmtree("New")

