#!/usr/bin/env python3

""" Helper script to bump the version and make git tags. For maintainer use only. """

from argparse import ArgumentParser
import re
from semantic_version import Version
from subprocess import call, check_output
import sys

DIRCOLORS_INIT = 'dircolors/__init__.py'

def get_version():
    with open(DIRCOLORS_INIT, 'r') as fp:
        for line in fp:
            if re.match(r'^__version__\b', line):
                globs = dict()
                exec(line, globs)
                ver_str = globs['__version__']
                return Version(ver_str)
    raise RuntimeError('unable to find __version__ in %s'%DIRCOLORS_INIT)

def update_version(new_ver):
    with open(DIRCOLORS_INIT, 'r') as fp:
        # buffer the whole file in memory before we start overwriting it
        init_lines = fp.read().splitlines()
    with open(DIRCOLORS_INIT, 'w') as fp:
        for line in init_lines:
            if re.match(r'^__version__\b', line):
                fp.write("__version__ = '%s'\n"%new_ver)
            else:
                fp.write(line + '\n')
    call(['git', 'commit', '-m', 'Version ' + str(new_ver), DIRCOLORS_INIT])

def tag_exists(tag):
    for line in check_output(['git', 'tag', '--list'], text=True).splitlines():
        if line == tag:
            return True
    return False

def main():
    parser = ArgumentParser()
    parser.add_argument('version', nargs='?', help='Version number (if omitted, bump patchlevel)')
    parser.add_argument('-d', '--dirty', action='store_true', help='Skip dirty "git status" check')
    args = parser.parse_args()

    if (not args.dirty) and check_output(['git', 'status', '--porcelain', '--untracked=no']):
        sys.exit('Error: git status is dirty, commit or stash first')

    current_ver = get_version()
    if not args.version:
        new_ver = current_ver.next_patch()
    else:
        new_ver = Version(args.version)

    tag_name = 'v' + str(new_ver)
    assert not tag_exists(tag_name)

    update_version(new_ver)
    call(['git', 'tag', '--edit', '-m', 'Version ' + str(new_ver), tag_name])

if __name__ == '__main__':
    sys.exit(main())
