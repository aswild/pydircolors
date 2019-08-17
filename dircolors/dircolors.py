# Dircolors, a Python library for colorizing and formatting filenames like GNU Coreutils'
# ls and dircolors programs.
# Requires python 3.3 or later

import os
import stat

from ._util import *

class Dircolors:
    def __init__(self, load=True):
        """ Initialize a Dircolors object. If load=True (the default), then try
        to load dircolors info from the LS_COLORS environment variable. """
        self.clear()
        if load:
            self.load_from_environ()

    def __bool__(self):
        return self._loaded

    @property
    def loaded(self):
        """ return a boolean indicating whether some valid dircolors data has been loaded """
        return self._loaded

    def clear(self):
        """ Clear the loaded data """
        self._loaded = False
        self._codes = {}
        self._extensions = {}

    def load_from_environ(self, envvar='LS_COLORS'):
        """ Load the dircolors database from an environment variable. By default,
        use LS_COLORS like the GNU Coreutils `ls` program.
        Returns True if data was successfully loaded, False otherwise (e.g. if
        envvar is unset). Regardless, the current database will be cleared """
        self.clear()
        lscolors = os.environ.get(envvar)
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
            return True
        return False

    def _format_code(self, text, code):
        """ format text with an lscolors code. Return text unmodified if code
        isn't found in the database """
        c = self._codes.get(code, None)
        if c:
            return '\033[%sm%s\033[%sm'%(c, text, self._codes.get('rs', '0'))
        return text

    def _format_ext(self, text, ext):
        """ Format text according to the given file extension.
        ext should not have a leading '.'
        text need not actually end in '.ext' """
        c = self._extensions.get(ext, '0')
        if c:
            return '\033[%sm%s\033[%sm'%(c, text, self._codes.get('rs', '0'))
        return text

    def format(self, file, cwd=None, follow_symlinks=False, show_target=True):
        """ Format and color the file given by the name `file`.

        If `cwd` is not None, it should be a string for the directory relative
        to which `file` is looked up, or an integer representing a directory
        descriptor (usually from `os.open()`).

        Use follow_symlinks to dereference symlinks entirely.
        Use show_target=True with follow_symlinks=False to format both the link name
        and its target in the format:
            linkname -> target
        With linkname formatted as a link color, and the link target formatted as its respective type.
        If the link target is another link, it will not be recursively dereferenced.
        """
        if not self.loaded:
            return file

        try:
            st = stat_at(file, cwd, follow_symlinks)
        except OSError as e:
            return '%s [Error stat-ing: %s]'%(file, e.strerror)

        mode = st.st_mode
        if (not follow_symlinks) and show_target and stat.S_ISLNK(mode):
            target_path = readlink_at(file, cwd)
            try:
                stat_at(target_path, cwd) # verify that link isn't broken
                target = self.format(target_path, cwd, False, False)
            except OSError:
                # format as "orphan"
                target = self._format_code(target_path, 'or') + ' [broken link]'
            return self._format_code(file, 'ln') + ' -> ' + target

        if stat.S_ISDIR(mode):
            if (mode & (stat.S_ISVTX | stat.S_IWOTH)) == (stat.S_ISVTX | stat.S_IWOTH):
                # sticky and world-writable
                return self._format_code(file, 'tw')
            elif mode & stat.S_ISVTX:
                # sticky but not world-writable
                return self._format_code(file, 'st')
            elif mode & stat.S_IWOTH:
                # world-writable but not sticky
                return self._format_code(file, 'ow')
            # normal directory
            return self._format_code(file, 'di')

        # special file?
        special_types = (
            (stat.S_IFIFO,  'pi'), # pipe (FIFO)
            (stat.S_IFSOCK, 'so'), # socket
            (stat.S_IFBLK,  'bd'), # block device
            (stat.S_IFCHR,  'cd'), # character device
            (stat.S_ISUID,  'su'), # setuid
            (stat.S_ISGID,  'sg'), # setgid
        )
        for mask, code in special_types:
            if (mode & mask) == mask:
                return self._format_code(file, code)

        # executable file?
        if mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH):
            return self._format_code(file, 'ex')

        # regular file, format according to its extension
        _, ext = os.path.splitext(file)
        if ext:
            return self._format_ext(file, ext)
        return file
