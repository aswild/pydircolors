# Copyright 2019 Allen Wild <allenwild93@gmail.com>
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=missing-docstring,protected-access

""" unit tests for the dircolors library """

from io import StringIO
import unittest

from dircolors import Dircolors
from dircolors._defaults import DEFAULT_LS_COLORS

__all__ = ['TestDircolors']

class TestDircolors(unittest.TestCase):
    def setUp(self):
        self.dc = Dircolors(load=False)

    def test_cleared(self):
        self.dc.clear()
        self.assertFalse(self.dc)
        self.assertFalse(self.dc.loaded)

    def test_defaults(self):
        self.dc.load_defaults()
        self.assertTrue(self.dc)
        self.assertTrue(self.dc.loaded)

    def test_generate_lscolors(self):
        self.dc.load_defaults()
        self.assertEqual(self.dc.generate_lscolors(), DEFAULT_LS_COLORS)

    def test_load_content(self):
        self.dc.clear()
        self.dc.load_from_dircolors(StringIO('LINK 01;36 # symlink\n'), strict=True)
        self.assertEqual(self.dc.generate_lscolors(), 'ln=01;36')

        self.dc.clear()
        with self.assertRaises(ValueError):
            self.dc.load_from_dircolors(StringIO('LINK 01;36\nfoo\n'), strict=True)

    def test_load_lscolors(self):
        self.dc.clear()
        self.dc.load_from_lscolors(DEFAULT_LS_COLORS)
        self.assertEqual(self.dc.generate_lscolors(), DEFAULT_LS_COLORS)
