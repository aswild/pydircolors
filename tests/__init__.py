""" tests for pydircolors and pyls """

from .test_dircolors import *

def full_suite():
    from unittest import TestSuite
    from unittest import defaultTestLoader as loader
    suite = TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(TestDircolors))
    return suite
