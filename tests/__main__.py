""" test runner wrapper: makes `python -m tests`
equivalent to `python -m unittest -v tests` """

from unittest import TextTestRunner
from . import full_suite

if __name__ == '__main__':
    # pylint: disable=invalid-name
    runner = TextTestRunner(verbosity=2)
    suite = full_suite()
    runner.run(suite)
