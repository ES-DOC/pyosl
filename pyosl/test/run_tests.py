import datetime
import os
import unittest

import pyosl

# Build the test suite from the tests found in the test files.
testsuite = unittest.TestSuite()
testsuite.addTests(unittest.TestLoader().discover('.', pattern='test_*.py'))
 
# Run the test suite.
# Run the test suite.
def run_test_suite(verbosity=2):
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
