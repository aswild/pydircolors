# pyls - a simple implementation of `ls` used to test python-dircolors
#
# Copyright 2019 Allen Wild <allenwild93@gmail.com>
# SPDX-License-Identifier: Apache-2.0

""" pyls - a simple implementation of `ls` used to test python-dircolors """

import argparse
import os
import sys

from ..dircolors import Dircolors

def main():
    """ pyls main function """
    # pylint: disable=invalid-name
    parser = argparse.ArgumentParser(prog='pyls', description='Python implementation of the "ls" command for testing dircolors')
    parser.add_argument('files', nargs='*', metavar='FILE', help='File or directories to list')
    args = parser.parse_args()

    files = args.files
    if not files:
        files = ['.']

    dc = Dircolors()
    for f in files:
        try:
            if os.path.isdir(f) and not os.path.islink(f):
                if f != '.' and len(files) > 1:
                    print(dc.format(f) + ':')
                for ff in sorted(os.listdir(f)):
                    print(dc.format(ff, f, show_target=True))
                print()
            else:
                print(dc.format(f, show_target=True))
        except OSError as e:
            print('%s: error: %s'%(f, e), file=sys.stderr)
