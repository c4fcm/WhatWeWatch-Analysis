import inspect
import os
import sys
import unittest

import networkx as nx
import numpy as np
import numpy.testing as nptest

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import stubs
import util

data = util.VideoData('testdata.csv')

class DataTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_counts(self):
        nptest.assert_allclose(stubs.counts, data.counts)

if __name__ == '__main__':
    unittest.main()
    