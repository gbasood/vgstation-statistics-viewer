import sys
import unittest

if __name__ == '__main__':  # pragma: no cover
    # unittest.main()
    test_suite = unittest.defaultTestLoader.discover(start_dir='.', pattern='*tests.py')
    test_runner = unittest.TextTestRunner(resultclass=TextTestResult)
    result = test_runner.run(test_suite)
    sys.exit(not result.wasSuccessful())
