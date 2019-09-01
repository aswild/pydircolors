""" test runner wrapper: makes `python -m tests` equivalent to `python -m unittest -v tests` """

from unittest import main

if __name__ == '__main__':
    main('tests', verbosity=2)
