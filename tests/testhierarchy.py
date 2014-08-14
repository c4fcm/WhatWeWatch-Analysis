import inspect
import os
import sys
import unittest

import numpy as np
import numpy.testing as nptest
import scipy as sp

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import hierarchy
import stubs
import util

data = util.VideoData.from_csv('testdata.csv')

class HierarchyTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_pdist_index(self):
        n, i, j = 5, 1, 3
        true_index = 5
        index = hierarchy.pdist_index(n, i, j)
        self.assertEqual(index, true_index)
        
    def test_pdist(self):
        pdist = hierarchy.pdist(data.counts).todense().tolist()
        nptest.assert_allclose(pdist, stubs.nat_pdist.todense().tolist())
        
    def test_vid_pdist(self):
        pdist = hierarchy.pdist(data.counts.transpose()).todense().tolist()
        true_pdist = stubs.vid_pdist.todense().tolist()
        nptest.assert_allclose(pdist, true_pdist)
    
    def test_linkage(self):
        linkage = hierarchy.linkage(stubs.nat_pdist).tolist()
        true_linkage = stubs.linkage.tolist()
        nptest.assert_allclose(linkage, true_linkage)
if __name__ == '__main__':
    unittest.main()
    