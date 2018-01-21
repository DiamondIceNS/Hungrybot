import unittest
import sys

if __name__ == "__main__":
    suite = unittest.TestLoader().discover("test")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(not result.wasSuccessful())
