import inspect
import os
import sys
import unittest

import numpy as np
import numpy.testing as nptest

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import findmigrant
import graph
import stubs
import util

class MigrantTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_mig_ex(self):
        mig_ex = findmigrant.migration_exposure(
            stubs.migration_stock[0]
            , stubs.migration_stock[1]
            , stubs.migration_pop[0]
            , stubs.migration_pop[1]
        )
        self.assertAlmostEqual(mig_ex, stubs.migration_ex)
        
if __name__ == '__main__':
    unittest.main()
    