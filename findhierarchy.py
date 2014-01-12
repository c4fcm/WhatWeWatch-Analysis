from __future__ import division

import ConfigParser
import csv
import sys
import time

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import scipy as sp
import scipy.spatial.distance as spdist
import scipy.cluster.hierarchy as sphier

import exposure
import graph
import util


def main():
    # Read config
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    
    exp_id = time.time()
    print "Beginning %f" % exp_id
    
    # Read data file, save country codes and country-video pairs
    filename = 'data/%s' % config.get('data', 'filename')
    data = util.VideoData(filename)
    
    # Calculate dendrogram
    labels = [data.country_lookup.get_token(x) for x in range(data.counts.shape[0])]
    labels = [util.country_name(x) for x in labels]
    d = spdist.pdist(np.array(data.counts), metric=exposure.distance)
    l = sphier.linkage(d, method='single',metric=exposure.distance)
    #l = exposure.linkage(data.counts)
    # Plot
    f = plt.figure(figsize=(16.5, 10.5))
    p = plt.plot()
    sphier.dendrogram(l, labels=labels, color_threshold=2.26)
    plt.title('Nations clustered by trending video exposure')
    y = sp.arange(0, 3.2, 0.4)
    #plt.axis([0, 57, 0, 3.0])
    #plt.yticks(y)
    plt.ylabel('Self-information (bits)')
    plt.tick_params('both', labelsize='12')
    plt.tight_layout()
    plt.show()
    util.create_result_dir('findhierarchy', exp_id)
    f.savefig('results/findhierarchy/%s/clusters.eps' % exp_id)

if __name__ == '__main__':
    main()
