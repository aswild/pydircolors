#!/usr/bin/env python3
# setup script for pydircolors
#
# Copyright 2019 Allen Wild <allenwild93@gmail.com>
# SPDX-License-Identifier: Apache-2.0

from setuptools import setup, find_packages

setup(
    name            = 'dircolors',
    version         = '0.0.1',
    author          = 'Allen Wild',
    author_email    = 'allenwild93@gmail.com',
    license         = 'Apache-2.0',
    url             = 'https://github.com/aswild/pydircolors',
    python_requires = ">=3.3",
    packages        = find_packages(),
    entry_points    = {
        'console_scripts': [
            'pyls = dircolors.pyls.__main__:main',
        ]
    },
    classifiers     = [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
