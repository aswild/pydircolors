# Dircolors, a Python library for colorizing and formatting filenames like GNU Coreutils'
# ls and dircolors programs.
# Requires python 3.3 or later
#
# Copyright 2019 Allen Wild <allenwild93@gmail.com>
# SPDX-License-Identifier: Apache-2.0

""" dircolors, a Python library to colorize filenames based on their type
for terminal use, like GNU ls and dircolors. """

from collections import OrderedDict
from io import StringIO, TextIOBase
import os
import stat

from ._defaults import DEFAULT_DIRCOLORS
from ._util import *

__all__ = ['Dircolors']

_CODE_MAP = OrderedDict()
def _init_code_map():
    """ mapping between the key name in the .dircolors file and the two letter
    code found in the LS_COLORS environment variable.
    Used for parsing .dircolors files. """
    # This code is wrapped in a function so we can disable pylint's whitespace check
    # on a limited scope.
    # pylint: disable=bad-whitespace
    _CODE_MAP['RESET']                  = 'rs'
    _CODE_MAP['DIR']                    = 'di'
    _CODE_MAP['LINK']                   = 'ln'
    _CODE_MAP['MULTIHARDLINK']          = 'mh'
    _CODE_MAP['FIFO']                   = 'pi'
    _CODE_MAP['SOCK']                   = 'so'
    _CODE_MAP['DOOR']                   = 'do'
    _CODE_MAP['BLK']                    = 'bd'
    _CODE_MAP['CHR']                    = 'cd'
    _CODE_MAP['ORPHAN']                 = 'or'
    _CODE_MAP['MISSING']                = 'mi'
    _CODE_MAP['SETUID']                 = 'su'
    _CODE_MAP['SETGID']                 = 'sg'
    _CODE_MAP['CAPABILITY']             = 'ca'
    _CODE_MAP['STICKY_OTHER_WRITABLE']  = 'tw'
    _CODE_MAP['OTHER_WRITABLE']         = 'ow'
    _CODE_MAP['STICKY']                 = 'st'
    _CODE_MAP['EXEC']                   = 'ex'

_init_code_map()
del _init_code_map

class Dircolors:
    """ Main dircolors class. Contains a database of formats corresponding to file types,
    modes, and extensions. Use the format() method to check a file and color it appropriately.
    """
    def __init__(self, load=True):
        """ Initialize a Dircolors object. If load=True (the default), then try
        to load dircolors info from the LS_COLORS environment variable.
        If no data is obtained from LS_COLORS, load the defaults.
        If load=False, don't even load defaults. """
        self._loaded = False
        self._codes = OrderedDict()
        self._extensions = OrderedDict()
        if load:
            if not self.load_from_environ():
                self.load_defaults()

    def __bool__(self):
        """ convenience method for checking whether this Dircolors object has loaded a database.
        Can be used like
            d = Dircolors()
            if d:
                d.format(somefile)
        """
        return self._loaded

    @property
    def loaded(self):
        """ return a boolean indicating whether some valid dircolors data has been loaded """
        return self._loaded

    def clear(self):
        """ Clear the loaded data """
        self._loaded = False
        self._codes.clear()
        self._extensions.clear()

    def load_from_lscolors(self, lscolors):
        """ Load the dircolors database from a string in the same format as the LS_COLORS
        environment variable.
        Returns True if data was successfully loaded, False otherwise (e.g. if
        envvar is unset). Regardless, the current database will be cleared """
        self.clear()
        if not lscolors:
            return False

        for item in lscolors.split(':'):
            try:
                code, color = item.split('=', 1)
            except ValueError:
                continue # no key=value, just ignore
            if code.startswith('*.'):
                self._extensions[code[1:]] = color
            else:
                self._codes[code] = color

        if self._codes or self._extensions:
            self._loaded = True
        return self._loaded

    def load_from_environ(self, envvar='LS_COLORS'):
        """ Load the dircolors database from an environment variable. By default,
        use LS_COLORS like the GNU Coreutils `ls` program.
        Returns True if data was successfully loaded, False otherwise (e.g. if
        envvar is unset). Regardless, the current database will be cleared. """
        return self.load_from_lscolors(os.environ.get(envvar))

    def load_from_dircolors(self, database, strict=False):
        """ Load the dircolors database from a GNU-compatible .dircolors file.
        May raise any of the usual OSError exceptions if filename doesn't exist
        or otherwise can't be read.

        database can be a string representing a filename, or a file-like object
        opened in text mode (i.e. a subclass of io.TextIOBase). To load from the
        contents of a .dircolors file, wrap it in an io.StringIO object.

        If strict is True, raise ValueError on the first unparsed line

        Returns a boolean indicating whether any data was loaded.
        The current database will always be cleared. """
        self.clear()
        if isinstance(database, str):
            file = open(database, 'r')
        elif isinstance(database, TextIOBase):
            file = database
        else:
            raise ValueError('database must be str or io.TextIOBase, not %s'%type(database))

        try:
            for line in file:
                # remove comments and skip empty lines
                line = line.split('#')[0].strip()
                if not line:
                    continue

                # make sure there's two space-separated fields
                split = line.split()
                if len(split) != 2:
                    if strict:
                        raise ValueError('Warning: unable to parse dircolors line "%s"'%line)
                    continue

                key, val = split
                if key == 'TERM':
                    continue # ignore TERM directives
                elif key in _CODE_MAP:
                    self._codes[_CODE_MAP[key]] = val
                elif key.startswith('.'):
                    self._extensions[key] = val
                elif strict:
                    raise ValueError('Warning: unable to parse dircolors line "%s"'%line)
                # elif not strict, skip

            if self._codes or self._extensions:
                self._loaded = True
            return self._loaded
        finally:
            file.close()

    def load_defaults(self):
        """ Load the default database. """
        self.clear()
        return self.load_from_dircolors(StringIO(DEFAULT_DIRCOLORS), True)

    def generate_lscolors(self):
        """ Output the database in the format used by the LS_COLORS environment variable. """
        if not self._loaded:
            return ''

        def gen_pairs():
            for pair in self._codes.items():
                yield pair
            for pair in self._extensions.items():
                # change .xyz to *.xyz
                yield '*' + pair[0], pair[1]

        return ':'.join('%s=%s'%pair for pair in gen_pairs())

    def _format_code(self, text, code):
        """ format text with an lscolors code. Return text unmodified if code
        isn't found in the database """
        val = self._codes.get(code, None)
        if val:
            return '\033[%sm%s\033[%sm'%(val, text, self._codes.get('rs', '0'))
        return text

    def _format_ext(self, text, ext):
        """ Format text according to the given file extension.
        ext must have a leading '.'
        text need not actually end in '.ext' """
        val = self._extensions.get(ext, '0')
        if val:
            return '\033[%sm%s\033[%sm'%(val, text, self._codes.get('rs', '0'))
        return text

    def format_mode(self, text, mode):
        """ Format and color the given text based on the given file mode.

        `mode` can be an integer, usually the st_mode field of an os.stat_result
        object obtained from os.stat() or similar function. It can also be an os.stat_result
        object, and the st_mode field will be extracted automatically.

        `text` is an arbitrary string which will be colored according to the bits
        set in `mode` and the colors database loaded in this Dircolors object.

        If `mode` represents a symlink, it will be formatted as such with no dereferencing
        (since this function doesn't know the file name) """
        if not self._loaded:
            return text

        if isinstance(mode, int):
            pass
        elif isinstance(mode, os.stat_result):
            mode = mode.st_mode
        else:
            raise ValueError('mode must be int or os.stat_result, not %s'%type(mode))

        if stat.S_ISDIR(mode):
            if (mode & (stat.S_ISVTX | stat.S_IWOTH)) == (stat.S_ISVTX | stat.S_IWOTH):
                # sticky and world-writable
                return self._format_code(text, 'tw')
            if mode & stat.S_ISVTX:
                # sticky but not world-writable
                return self._format_code(text, 'st')
            if mode & stat.S_IWOTH:
                # world-writable but not sticky
                return self._format_code(text, 'ow')
            # normal directory
            return self._format_code(text, 'di')

        # special file?
        # pylint: disable=bad-whitespace
        special_types = (
            (stat.S_IFLNK,  'ln'), # symlink
            (stat.S_IFIFO,  'pi'), # pipe (FIFO)
            (stat.S_IFSOCK, 'so'), # socket
            (stat.S_IFBLK,  'bd'), # block device
            (stat.S_IFCHR,  'cd'), # character device
            (stat.S_ISUID,  'su'), # setuid
            (stat.S_ISGID,  'sg'), # setgid
        )
        for mask, code in special_types:
            if (mode & mask) == mask:
                return self._format_code(text, code)

        # executable file?
        if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            return self._format_code(text, 'ex')

        # regular file, format according to its extension
        _, ext = os.path.splitext(text)
        if ext:
            return self._format_ext(text, ext)
        return text

    def format(self, file, cwd=None, follow_symlinks=False, show_target=False):
        """ Format and color the file given by the name `file`.

        If `cwd` is not None, it should be a string for the directory relative
        to which `file` is looked up, or an integer representing a directory
        descriptor (usually from `os.open()`).

        Use follow_symlinks to dereference symlinks entirely.
        Use show_target=True with follow_symlinks=False to format both the link name
        and its target in the format:
            linkname -> target
        With linkname formatted as a link color, and the link target formatted as its respective
        type. If the link target is another link, it will not be recursively dereferenced. """
        if not self.loaded:
            return file

        try:
            statbuf = stat_at(file, cwd, follow_symlinks)
        except OSError as e:
            return '%s [Error stat-ing: %s]'%(file, e.strerror)

        mode = statbuf.st_mode
        if (not follow_symlinks) and show_target and stat.S_ISLNK(mode):
            target_path = readlink_at(file, cwd)
            try:
                stat_at(target_path, cwd) # check for broken link
                target = self.format(target_path, cwd, False, False)
            except OSError:
                # format as "orphan"
                target = self._format_code(target_path, 'or') + ' [broken link]'
            return self._format_code(file, 'ln') + ' -> ' + target

        return self.format_mode(file, mode)
