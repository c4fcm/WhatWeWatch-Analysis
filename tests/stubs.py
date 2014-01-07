from __future__ import division

import inspect
import os
import sys

import networkx as nx
import numpy as np

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)
import util

# Country-video counts for test data
counts = np.array([
    [1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
    [3,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
    [0,3,0,0,0,0,0,0,0,1,1,1,0,0,0],
    [0,0,0,0,0,0,3,0,0,3,0,0,0,0,0],
    [0,0,0,0,0,0,1,2,0,0,0,0,1,1,1],
])
country_lookup = util.Lookup(['a', 'b', 'c', 'd', 'e'])

# Directed exposure graph for test data
dir_ex = nx.DiGraph()
dir_ex.add_edge(0, 1, weight=1/6)
dir_ex.add_edge(0, 2, weight=1/6)
dir_ex.add_edge(1, 0, weight=1/2)
dir_ex.add_edge(1, 3, weight=1/6)
dir_ex.add_edge(1, 4, weight=1/3)
dir_ex.add_edge(2, 0, weight=1/2)
dir_ex.add_edge(2, 3, weight=1/6)
dir_ex.add_edge(3, 1, weight=1/2)
dir_ex.add_edge(3, 2, weight=1/2)
dir_ex.add_edge(3, 4, weight=1/2)
dir_ex.add_edge(4, 1, weight=1/2)
dir_ex.add_edge(4, 3, weight=1/6)

# Symmetric exposure graph for test data
sym_ex = nx.Graph()
sym_ex.add_edge(0, 1, weight=1/3, distance=1.09861228867)
sym_ex.add_edge(0, 2, weight=1/3, distance=1.09861228867)
sym_ex.add_edge(1, 3, weight=1/3, distance=1.09861228867)
sym_ex.add_edge(2, 3, weight=1/3, distance=1.09861228867)
sym_ex.add_edge(3, 4, weight=1/3, distance=1.09861228867)
sym_ex.add_edge(1, 4, weight=5/12, distance=0.87546873735)

# Directed exposure graph weights
in_degree = [1, 7/6, 2/3, 1/2, 5/6]
out_degree = [1/3, 1, 2/3, 3/2, 2/3]
degree = [1/6, 13/12, 2/3, 1, 3/4]

# Country name stub
def country_name(name):
    return name

