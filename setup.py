#!/usr/bin/env python3
# setup script for pydircolors
#
# Copyright 2019 Allen Wild <allenwild93@gmail.com>
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=bad-whitespace,missing-docstring

import os
import re
from setuptools import setup

def get_version():
    """ get the dircolors version by regex-parsing __init__.py
    see https://packaging.python.org/guides/single-sourcing-package-version """
    mydir = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(mydir, 'dircolors', '__init__.py')
    with open(filename, 'r') as fp:
        for line in fp:
            m = re.match(r'^__version__\s*=\s*[\'"](.*)[\'"]', line)
            if m:
                return m.group(1)
    raise RuntimeError('Unable to find version in "%s"'%filename)

def read_readme():
    with open('README.md', 'r') as fp:
        return fp.read()

setup(
    name            = 'dircolors',
    version         = get_version(),
    author          = 'Allen Wild',
    author_email    = 'allenwild93@gmail.com',
    description     = 'Python library to colorize and format file names based on type',
    long_description= read_readme(),
    long_description_content_type = 'text/markdown',
    license         = 'Apache-2.0',
    url             = 'https://github.com/aswild/pydircolors',
    python_requires = ">=3.3",
    packages        = ['dircolors'],
    test_suite      = 'tests.full_suite',
    entry_points = {
        'console_scripts': [
            'pyls = dircolors.pyls.__main__:main',
        ]
    },
    classifiers = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
    ]
)
