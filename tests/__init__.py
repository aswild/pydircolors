""" tests for pydircolors and pyls """

from .test_dircolors import *

def full_suite():
    """ return a TestSuite of all the dircolors test cases """
    from unittest import TestSuite
    from unittest import defaultTestLoader as loader
    suite = TestSuite()
    suite.addTest(loader.loadTestsFromTestCase(TestDircolors))
    return suite
