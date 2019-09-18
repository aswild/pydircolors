# Copyright 2019 Allen Wild <allenwild93@gmail.com>
# SPDX-License-Identifier: Apache-2.0
#
# pylint: disable=missing-docstring,protected-access

""" unit tests for the dircolors library """

from io import StringIO
import os
import shutil
import stat
import sys
import tempfile
import unittest

from dircolors import Dircolors
from dircolors._defaults import DEFAULT_LS_COLORS

__all__ = ['TestDircolorsDB', 'TestDircolorsFormat', 'TestDircolorsFile']

# Test debugging - print some extra output, and don't delete temporary directories
_DEBUG_ENABLE = False
def _debug(*args):
    if _DEBUG_ENABLE:
        print(*args, file=sys.stderr)

def _wrap(text, color, reset='\033[0m'):
    """ wrap text between color and reset, unless color is None, then return text """
    if color:
        return '\033[%sm%s%s'%(color, text, reset)
    else:
        return text

class TestDircolorsDB(unittest.TestCase):
    """ Tests for the basic infrastructure, loading dircolors data, and
    generating LS_COLORS environment variables. """
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

class TestDircolorsFormat(unittest.TestCase):
    """ Lower level tests for format_mode with text and a file type+mode int directly """
    def setUp(self):
        self.dc = Dircolors(load=False)

    def test_empty(self):
        self.dc.clear()
        self.assertEqual(self.dc.format_mode('dirname', 0o040755), 'dirname')
        self.assertEqual(self.dc.format_mode('filename', 0o100755), 'filename')

    def test_format_mode(self):
        self.dc.load_defaults()
        self.assertEqual(self.dc.format_mode('dirname', 0o040755), _wrap('dirname', '01;34'))
        self.assertEqual(self.dc.format_mode('filename', 0o100644), 'filename')
        self.assertEqual(self.dc.format_mode('filename', 0o100755), _wrap('filename', '01;32'))
        self.assertEqual(self.dc.format_mode('linkname', 0o120777), _wrap('linkname', '01;36'))
        self.assertEqual(self.dc.format_mode('filename.tar', 0o100644),
                                             '\033[01;31mfilename.tar\033[0m')

class TestDircolorsFile(unittest.TestCase):
    """ Higher level tests on actual files. """

    # 3-tuple of files to create in our test dir
    # 0: name
    # 1: mode to create with, or None to do custom stuff
    # 2: expected mode for it to format as, or None for no format
    _test_files = [
        ('normalfile',  0o644,  None),
        ('execfile',    0o755,  '01;32'),
        ('tarfile.tar', 0o644,  '01;31'),
        ('image.png',   0o644,  '01;35'),
        ('suidfile',    0o4755, '37;41'),
        ('subdir',      None,   '01;34'),
        ('link.png',    None,   '01;36'),
    ]

    @classmethod
    def setUpClass(cls):
        """ Create a temporary directory and populate it with some files. """
        cls.dc = Dircolors()
        cls.dc.load_defaults()
        cls.tmpdir = tempfile.mkdtemp()
        _debug('testing in %s'%cls.tmpdir)

        # create normal files
        for filename, mode, _ in cls._test_files:
            if mode:
                file = os.path.join(cls.tmpdir, filename)
                fd = os.open(file, os.O_WRONLY | os.O_CREAT, mode)
                os.close(fd)

        # make special files (and a subdirectory)
        os.mkdir(cls.tmpdir + '/subdir')
        os.symlink('image.png', cls.tmpdir + '/link.png')

    @classmethod
    def tearDownClass(cls):
        """ Clean up the temporary directory unless debug mode is enabled """
        if _DEBUG_ENABLE:
            _debug('not deleting %s'%cls.tmpdir)
        else:
            shutil.rmtree(cls.tmpdir)

    def test_files(self):
        for filename, _, fmt in self._test_files:
            file = os.path.join(self.tmpdir, filename)
            with self.subTest(file=file, fmt=fmt):
                self.assertEqual(self.dc.format(file), _wrap(file, fmt))

    def test_with_cwd(self):
        for filename, _, fmt in self._test_files:
            with self.subTest(file=filename, fmt=fmt):
                self.assertEqual(self.dc.format(filename, cwd=self.tmpdir), _wrap(filename, fmt))

    def test_follow_symlink(self):
        file = os.path.join(self.tmpdir, 'link.png')
        self.assertEqual(self.dc.format(file, follow_symlinks=True), _wrap(file, '01;35'))

    def test_symlink_target(self):
        file = os.path.join(self.tmpdir, 'link.png')
        self.assertEqual(self.dc.format(file, show_target=True),
                         '\033[01;36m' + file + '\033[0m -> \033[01;35mimage.png\033[0m')
