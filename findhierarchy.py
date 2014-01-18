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

exp_id = time.time()

# Threshold for defining hierarchical clusters
hierarchy_threshold = 2.26

def main():
    # Read config
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    
    print "Beginning %f" % exp_id
    
    # Read data file, save country codes and country-video pairs
    filename = 'data/%s' % config.get('data', 'filename')
    data = util.VideoData(filename)
    
    # Calculate dendrogram
    d = spdist.pdist(np.array(data.counts), metric=exposure.distance)
    l = sphier.linkage(d, method='single',metric=exposure.distance)
    #l = exposure.linkage(data.counts)
    
    # Plot
    plot_dendrogram(data, l)
    
    # Find average exposure within and across clusters
    cluster_exposure(data, l)

def plot_dendrogram(data, l):
    labels = [data.country_lookup.get_token(x) for x in range(data.counts.shape[0])]
    labels = [util.country_name(x) for x in labels]
    f = plt.figure(figsize=(16.5, 10.5))
    p = plt.plot()
    sphier.dendrogram(l, labels=labels, color_threshold=hierarchy_threshold)
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

def cluster_exposure(data, l):
    n = data.counts.shape[0]
    clusters = get_clusters(l)
    cluster_exposure = []
    for i, cluster in clusters.iteritems():
        if len(cluster) < 2:
            continue
        # Calculate internal exposure
        internal = 0
        m = 0
        for head in cluster:
            for tail in cluster:
                if tail >= head:
                    continue
                m += 1
                internal += exposure.symmetric(data.counts[head], data.counts[tail])
        internal /= m
        external = 0
        m = 0
        complement = [x for x in range(n) if x not in cluster]
        for head in cluster:
            for tail in complement:
                external += exposure.symmetric(data.counts[head], data.counts[tail])
                m += 1
        external /= m
        names = ';'.join([util.country_name(data.country_lookup.get_token(x)) for x in cluster])
        cluster_exposure.append((names, internal, external, -1*np.log2(internal), -1*np.log2(external)))
    fields = ('Countries', 'Mean internal exposure', 'Mean external exposure', 'Internal self-information', 'External self-information')
    util.write_results_csv('findhierarchy', exp_id, 'cluster_exposure', cluster_exposure, fields)

def get_clusters(l):
    n = l.shape[0] + 1
    clusters = dict((i, set([i])) for i in range(n))
    for i, step in enumerate(l):
        tail, head, dist, size = step
        if dist > hierarchy_threshold:
            break;
        clusters[n + i] = clusters[int(tail)].union(clusters[int(head)])
        del clusters[int(tail)]
        del clusters[int(head)]
    return clusters
    
if __name__ == '__main__':
    main()
