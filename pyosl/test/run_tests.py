import datetime
import os
import unittest

# Build the test suite from the tests found in the test files.
# We don't do the UML tests at the same time since they build a different ontology
# (an ontology of UML views)

testsuite = unittest.TestSuite()
testsuite.addTests(unittest.TestLoader().discover('.', pattern='test_*.py'))


def run_test_suite(verbosity=2):
    ''' Runs the test suite'''
    runner = unittest.TextTestRunner(verbosity=verbosity)
    runner.run(testsuite)


if __name__ == '__main__':
    print('---------------')
    print('PYOSL TEST SUITE')
    print('---------------')
    print('Run date:', datetime.datetime.now())
    print('')
    print('Running tests from', os.path.abspath(os.curdir))
    print('')
    
    run_test_suite()
