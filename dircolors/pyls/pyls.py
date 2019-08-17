# pyls - a simple implementation of `ls` used to test python-dircolors
#
# Copyright 2019 Allen Wild <allenwild93@gmail.com>
# SPDX-License-Identifier: Apache-2.0

import os
import sys

from ..dircolors import Dircolors

def main():
    files = sys.argv[1:]
    if not files:
        files = ['.']

    d = Dircolors()
    for f in files:
        if os.path.isdir(f) and not os.path.islink(f):
            if f != '.':
                print(d.format(f) + ':')
            for ff in sorted(os.listdir(f)):
                print(d.format(ff, f, show_target=True))
            print()
        else:
            print(d.format(f, show_target=True))

