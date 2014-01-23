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
import graph
import stubs
import util

data = util.VideoData.from_csv('testdata.csv')

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

    def test_symmetric_distance(self):
        try:
            old_country_name = util.country_name
            util.country_name = stubs.country_name
            sym_ex = findexposure.symmetric_exposure(stubs.counts, stubs.country_lookup)
            for tail, head, d in stubs.sym_ex.edges(data=True):
                self.assertAlmostEqual(d['distance'], sym_ex.edge[tail][head]['distance'])
        finally:
            util.country_name = old_country_name
    
    def test_in_degree(self):
        in_degree = [y for x,y in sorted(graph.weighted_in_degree_centrality(stubs.dir_ex).items())]
        nptest.assert_allclose(in_degree, stubs.in_degree)

    def test_out_degree(self):
        out_degree = [y for x,y in sorted(graph.weighted_out_degree_centrality(stubs.dir_ex).items())]
        nptest.assert_allclose(out_degree, stubs.out_degree)

    def test_degree(self):
        degree = [y for x,y in sorted(graph.weighted_degree_centrality(stubs.sym_ex).items())]
        nptest.assert_allclose(degree, stubs.degree)
        
    def test_right_eigenvector(self):
        eigenvector_right = [y for x,y in sorted(nx.eigenvector_centrality(stubs.dir_ex).items())]
        nptest.assert_allclose(eigenvector_right, stubs.eigenvector_right, rtol=1e-3)
    
    def test_left_eigenvector(self):
        eigenvector_left = [y for x,y in sorted(nx.eigenvector_centrality(stubs.dir_ex.reverse()).items())]
        nptest.assert_allclose(eigenvector_left, stubs.eigenvector_left, rtol=1e-3)
    
    def test_eigenvector(self):
        eigenvector = [y for x,y in sorted(nx.eigenvector_centrality(stubs.sym_ex).items())]
        nptest.assert_allclose(eigenvector, stubs.eigenvector, rtol=1e-3)

if __name__ == '__main__':
    unittest.main()
    