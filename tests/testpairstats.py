import inspect
import os
import sys
import unittest

import numpy as np
import numpy.testing as nptest

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import findpairstats
import graph
import stubs
import util

class MigrantTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def test_mig_ex(self):
        mig_ex = findpairstats.migrant_exposure_pair(
            stubs.migration_to_tail
            , stubs.migration_to_head
            , stubs.migration_tail_pop
            , stubs.migration_head_pop
        )
        self.assertAlmostEqual(mig_ex, stubs.migration_ex)
    
    def test_language_true(self):
        common = findpairstats.language_common_pair(stubs.language_usa, stubs.language_spain)
        self.assertEqual(common, True)
        
    def test_language_false(self):
        common = findpairstats.language_common_pair(stubs.language_usa, stubs.language_andorra)
        self.assertEqual(common, False)
        
if __name__ == '__main__':
    unittest.main()
    