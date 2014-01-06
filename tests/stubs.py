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

# Directed exposure graph for test data
dir_ex = nx.DiGraph()
dir_ex.add_edge('a', 'b', weight=1/6)
dir_ex.add_edge('a', 'c', weight=1/6)
dir_ex.add_edge('b', 'a', weight=1/2)
dir_ex.add_edge('b', 'd', weight=1/6)
dir_ex.add_edge('b', 'e', weight=1/3)
dir_ex.add_edge('c', 'a', weight=1/2)
dir_ex.add_edge('c', 'd', weight=1/6)
dir_ex.add_edge('d', 'b', weight=1/2)
dir_ex.add_edge('d', 'c', weight=1/2)
dir_ex.add_edge('d', 'e', weight=1/2)
dir_ex.add_edge('e', 'b', weight=1/2)
dir_ex.add_edge('e', 'd', weight=1/6)

# Directed exposure graph weights
in_degree = [1, 7/6, 2/3, 1/2, 5/6]
out_degree = [1/3, 1, 2/3, 3/2, 2/3]



