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

import findexposure
import stubs
import util

data = util.VideoData('testdata.csv')

class DataTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_counts(self):
        nptest.assert_allclose(stubs.counts, data.counts)
        
    def test_directed_exposure(self):
        try:
            old_country_name = util.country_name
            util.country_name = stubs.country_name
            dir_ex = findexposure.directed_exposure(stubs.counts, stubs.country_lookup)
            for tail, head, d in stubs.dir_ex.edges(data=True):
                self.assertAlmostEqual(d['weight'], dir_ex.edge[tail][head]['weight'])
        finally:
            util.country_name = old_country_name

    def test_symmetric_exposure(self):
        try:
            old_country_name = util.country_name
            util.country_name = stubs.country_name
            sym_ex = findexposure.symmetric_exposure(stubs.counts, stubs.country_lookup)
            for tail, head, d in stubs.sym_ex.edges(data=True):
                self.assertAlmostEqual(d['weight'], sym_ex.edge[tail][head]['weight'])
        finally:
            util.country_name = old_country_name

if __name__ == '__main__':
    unittest.main()
    