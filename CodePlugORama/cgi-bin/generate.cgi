#!/usr/bin/env python3
# -*- coding: utf8 -*-

import cgi
import os
import sys

def main():
    global device, baud, foo

    print('Content-type: text/plain')
    print()
    form = cgi.FieldStorage()
    print(form.keys());
    for key in form.keys():
        print(f"{key}: {form.getvalue(key)}")
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt as e:
        print()
        sys.exit(1)
