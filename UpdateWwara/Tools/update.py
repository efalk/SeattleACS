#!/usr/bin/env python3
# -*- coding: utf8 -*-

"""Simple script to download the latest repeater list from WWARA and
process it into Chirp and RT Systems code plugs.

Exit codes:
    0 success
    1 success, but nothing needs to be done
    2 user error
    3 system error
"""

import csv
import errno
import glob
import os
import re
import shutil
import signal
import sys
import zipfile

from ezt import Template

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
    filename = os.path.basename(filename[0])

    if os.path.exists(filename):
        # Nothing to do
        print(f'File "{filename}" has already been processed, nothing to do')
        return 1

    if not os.path.exists("Chirp"):
        os.mkdir("Chirp")

    if not os.path.exists("RtSys"):
        os.mkdir("RtSys")

    cmd = f'./Tools/Wwara2Csv.py -v --Chirp "New/{filename}" > Chirp/wwara_chirp.csv'
    if verbose: print("About to execute", cmd)
    rval = os.system(cmd)
    if rval:
        print(f"Generate Chirp failed, ret={rval}", file=sys.stderr)
        return 3

    cmd = f'./Tools/Wwara2Csv.py -v --RtSys "New/{filename}" > RtSys/wwara_rt.csv'
    if verbose: print("About to execute", cmd)
    rval = os.system(cmd)
    if rval:
        print(f"Generate RT Sys failed, ret={rval}", file=sys.stderr)
        return 3

    csvfiles = glob.glob('*.csv')
    for file in csvfiles:
        os.unlink(file)

    os.rename(os.path.join("New", filename), filename)

    # Step 2: update the web page

    data = {}
    mo = re.match(r'''WWARA-rptrlist-(\d\d\d\d)(\d\d)(\d\d).csv''', filename)
    if not mo:
        print(f"Error: unable to extract date from \"{filename}\"")
        return 3

    data["year"] = mo.group(1)
    data["month"] = mo.group(2)
    data["day"] = mo.group(3)

    template = Template("index.ezt")

    ofile = open("index.html", "w")
    template.generate(ofile, data)

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

