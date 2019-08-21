# private utility functions for pydircolors
#
# Copyright 2019 Allen Wild <allenwild93@gmail.com>
# SPDX-License-Identifier: Apache-2.0

""" private/internal utility functions for pydircolors """

import os

__all__ = ['stat_at', 'readlink_at']

def stat_at(file, cwd=None, follow_symlinks=False):
    """ helper function to call os.stat on a file relative to a given directory.
    cwd should be a string, and will be opened as read-only (then closed), or an integer
    for an already-open directory file descriptor (which won't be closed).
    os.open or os.stat may raise various errors, which are passed on. """
    if isinstance(cwd, str):
        dirfd = os.open(cwd, os.O_RDONLY)
        need_to_close = True
    elif cwd is None or isinstance(cwd, int):
        dirfd = cwd
        need_to_close = False
    else:
        raise ValueError('cwd must be str, int, or None')

    try:
        return os.stat(file, dir_fd=dirfd, follow_symlinks=follow_symlinks)
    finally:
        if need_to_close:
            os.close(dirfd)

def readlink_at(file, cwd=None):
    """ helper function to call os.readlink on a file relative to a given directory.
    cwd should be a string, and will be opened as read-only (then closed), or an integer
    for an already-open directory file descriptor (which won't be closed).
    os.open or os.readlink may raise various errors, which are passed on. """
    if isinstance(cwd, str):
        dirfd = os.open(cwd, os.O_RDONLY)
        need_to_close = True
    elif cwd is None or isinstance(cwd, int):
        dirfd = cwd
        need_to_close = False
    else:
        raise ValueError('cwd must be str, int, or None')

    try:
        return os.readlink(file, dir_fd=dirfd)
    finally:
        if need_to_close:
            os.close(dirfd)
