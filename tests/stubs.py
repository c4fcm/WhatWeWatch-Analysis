from __future__ import division

import inspect
import os
import sys

import networkx as nx
import numpy as np
import scipy as sp
import scipy.sparse as spsparse

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

import hierarchy
import util

# Sample raw country, video, date data
raw = [
    ('2014-07-01', 'usa', 'A')
    , ('2014-07-02', 'can', 'A')
    , ('2014-07-03', 'aus', 'A')
    , ('2014-07-01', 'usa', 'B')
    , ('2014-07-08', 'usa', 'B')
    , ('2014-07-01', 'usa', 'C')
    , ('2014-07-09', 'usa', 'C')
]
span_by_vid = { 'A': 3.0, 'B': 8.0, 'C': 1.0 }
spread_by_vid = { 'A': 3, 'B': 1, 'C': 1 }

# Country-video counts for test data
counts = np.array([
    [1,1,1,1,1,1,0,0,0,0,0,0,0,0,0],
    [3,0,0,0,0,0,1,1,1,0,0,0,0,0,0],
    [0,3,0,0,0,0,0,0,0,1,1,1,0,0,0],
    [0,0,0,0,0,0,3,0,0,3,0,0,0,0,0],
    [0,0,0,0,0,0,1,2,0,0,0,0,1,1,1],
])
country_lookup = util.Lookup(['a', 'b', 'c', 'd', 'e'])

# Condensed distance matrix for countries
nat_pdist = spsparse.dok_matrix((10, 1))
nat_pdist[0,0] = -1/3
nat_pdist[1,0] = -1/3
nat_pdist[5,0] = -1/3
nat_pdist[6,0] = -5/12
nat_pdist[7,0] = -1/3
nat_pdist[9,0] = -1/3

# Condensed distance matrix for videos
vid_pdist = spsparse.dok_matrix((105,1))
vid_pdist[hierarchy.pdist_index(15,0,1), 0] = -1/4
vid_pdist[hierarchy.pdist_index(15,0,2), 0] = -2/5
vid_pdist[hierarchy.pdist_index(15,0,3), 0] = -2/5
vid_pdist[hierarchy.pdist_index(15,0,4), 0] = -2/5
vid_pdist[hierarchy.pdist_index(15,0,5), 0] = -2/5
vid_pdist[hierarchy.pdist_index(15,0,6), 0] = -4/9
vid_pdist[hierarchy.pdist_index(15,0,7), 0] = -4/7
vid_pdist[hierarchy.pdist_index(15,0,8), 0] = -4/5
vid_pdist[hierarchy.pdist_index(15,1,2), 0] = -2/5
vid_pdist[hierarchy.pdist_index(15,1,3), 0] = -2/5
vid_pdist[hierarchy.pdist_index(15,1,4), 0] = -2/5
vid_pdist[hierarchy.pdist_index(15,1,5), 0] = -2/5
vid_pdist[hierarchy.pdist_index(15,1,9), 0] = -1/2
vid_pdist[hierarchy.pdist_index(15,1,10), 0] = -4/5
vid_pdist[hierarchy.pdist_index(15,1,11), 0] = -4/5
vid_pdist[hierarchy.pdist_index(15,2,3), 0] = -1
vid_pdist[hierarchy.pdist_index(15,2,4), 0] = -1
vid_pdist[hierarchy.pdist_index(15,2,5), 0] = -1
vid_pdist[hierarchy.pdist_index(15,3,4), 0] = -1
vid_pdist[hierarchy.pdist_index(15,3,5), 0] = -1
vid_pdist[hierarchy.pdist_index(15,4,5), 0] = -1
vid_pdist[hierarchy.pdist_index(15,6,7), 0] = -5/8
vid_pdist[hierarchy.pdist_index(15,6,8), 0] = -1/3
vid_pdist[hierarchy.pdist_index(15,6,9), 0] = -2/3
vid_pdist[hierarchy.pdist_index(15,6,12), 0] = -1/3
vid_pdist[hierarchy.pdist_index(15,6,13), 0] = -1/3
vid_pdist[hierarchy.pdist_index(15,6,14), 0] = -1/3
vid_pdist[hierarchy.pdist_index(15,7,8), 0] = -1/2
vid_pdist[hierarchy.pdist_index(15,7,12), 0] = -3/4
vid_pdist[hierarchy.pdist_index(15,7,13), 0] = -3/4
vid_pdist[hierarchy.pdist_index(15,7,14), 0] = -3/4
vid_pdist[hierarchy.pdist_index(15,9,10), 0] = -2/5
vid_pdist[hierarchy.pdist_index(15,9,11), 0] = -2/5
vid_pdist[hierarchy.pdist_index(15,10,11), 0] = -1
vid_pdist[hierarchy.pdist_index(15,12,13), 0] = -1
vid_pdist[hierarchy.pdist_index(15,12,14), 0] = -1
vid_pdist[hierarchy.pdist_index(15,13,14), 0] = -1

# Nation clustering result
linkage = np.array([
    [1, 4, -5/12, 2]
    , [0, 2, -1/3, 2]
    , [3, 5, -1/3, 3]
    , [6, 7, -1/3, 5]
])

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

# Symmetric co-affiliation graph for test data
sym_ex = nx.Graph()
sym_ex.add_edge(0, 1, weight=1/3, distance=1.58496250072)
sym_ex.add_edge(0, 2, weight=1/3, distance=1.58496250072)
sym_ex.add_edge(1, 3, weight=1/3, distance=1.58496250072)
sym_ex.add_edge(2, 3, weight=1/3, distance=1.58496250072)
sym_ex.add_edge(3, 4, weight=1/3, distance=1.58496250072)
sym_ex.add_edge(1, 4, weight=5/12, distance=1.26303440583)

# Co-affiliation graph degrees
in_degree = [1, 7/6, 2/3, 1/2, 5/6]
out_degree = [1/3, 1, 2/3, 3/2, 2/3]
degree = [2/3, 13/12, 2/3, 1, 3/4]

# Co-affiliation graph eigenvector centralities
eigenvector_right = [0.1482, 0.4397, 0.2514, 0.7272, 0.4389]
eigenvector_left = [0.5639, 0.5755, 0.3009, 0.2795, 0.4268]
eigenvector = [0.3369, 0.5492, 0.3273, 0.5144, 0.4617]

# Migration and population test data
migration_head_pop = 8389771
migration_tail_pop = 4367800
migration_to_head = 320
migration_to_tail = 1464
migration_ex = 1.3984e-4

# Mean number of peers
mean_peers = np.array([2, 6, 4, 9, 4]) / 6.0

# Language data
language_usa = set(['english','spanish','hawaiian'])
language_spain = set(['castilian','spanish','catalan','galician','basque','valencian'])
language_andorra = set(['catalan', 'french', 'castilian', 'portuguese'])

# Country name stub
def country_name(name):
    return name

