from __future__ import division

import ConfigParser
import csv
import datetime
import sys
import time

import math
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import scipy as sp
import scipy.cluster.hierarchy as sphier
import scipy.misc as spmisc
import scipy.spatial.distance as spdist

import exposure
import graph
import hierarchy
import slink
import util

exp_id = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

# Threshold for defining hierarchical clusters
hierarchy_threshold = 2.26

def main():
    # Read config
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    
    print "Beginning %s" % exp_id
    
    # Read data file, save country codes and country-video pairs
    filename = 'data/%s' % config.get('data', 'filename')
    data = util.VideoData.from_csv(filename)
    
    # Calculate nation dendrogram
    d = spdist.pdist(np.array(data.counts), metric=exposure.distance)
    l = sphier.linkage(d, method='single',metric=exposure.distance)
    #l = exposure.linkage(data.counts)
    # Plot
    plot_dendrogram(data, l)
    save_clusters(data, l)
    # Find average exposure within and across clusters
    cluster_exposure(data, l)
    save_linkage_tree(data, l)
    
    # Calculate video dendrogram
    print "Clustering videos"
    video_counts = data.counts.transpose()
    #video_counts = video_counts[0:100,:]
    p, b = slink.linkage(video_counts, lambda x,y: 1.0 - exposure.symmetric(x,y))
    print "Converting to scipy style"
    l = slink.pointer_to_scipy(p, b)
    save_linkage(l)
    print "Writing confusion matrix"
    save_confusion_matrix(data, l)

def plot_dendrogram(data, l):
    labels = [data.country_lookup.get_token(x) for x in range(data.counts.shape[0])]
    labels = [util.country_name(x) for x in labels]
    for i, label in enumerate(labels):
        if labels[i] == 'United Arab Emirates':
            labels[i] = 'UAE'
    f = plt.figure(figsize=(7, 4))
    p = plt.plot()
    sphier.dendrogram(l, labels=labels, color_threshold=hierarchy_threshold)
    fdtitle = {'fontsize':10}
    fdaxis = {'fontsize':8}
    plt.title('Nations clustered by trending video exposure', fontdict=fdtitle)
    y = sp.arange(1.0, 4.5, 0.5)
    plt.ylim(0.8, 4.2)
    plt.yticks(y)
    plt.ylabel('Exposure distance (bits)', fontdict=fdaxis)
    plt.tick_params('both', labelsize='7')
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

def save_clusters(data, l):
    clusters = get_clusters(l)
    results = []
    fields = ('Id', 'Cluster')
    for i, cluster in clusters.iteritems():
        for c in cluster:
            code = data.country_lookup.get_token(c)
            results.append((code, i))
    util.write_results_csv('findhierarchy', exp_id, 'clusters', results, fields)
    
def save_linkage_tree(data, l):
    '''Write the edges in the linkage tree to a file.'''
    results = []
    fields = ('Source', 'Target', 'Type', 'Id', 'Label', 'Weight')
    # Find the source/target for each shortest path
    n = l.shape[0] + 1
    clusters = dict((i, set([i])) for i in range(n))
    for i, step in enumerate(l):
        tail, head, dist, size = step
        shortest = -1
        for t in clusters[tail]:
            for h in clusters[head]:
                ex = exposure.symmetric(data.counts[t,:], data.counts[h,:])
                d = exposure.distance(data.counts[t,:], data.counts[h,:])
                if shortest < 0 or d < shortest:
                    link_tail = data.country_lookup.get_token(t)
                    link_head = data.country_lookup.get_token(h)
                    shortest = d
                    shortest_ex = ex
        results.append((link_tail, link_head, 'Undirected', '', '', shortest_ex))
        clusters[n + i] = clusters[int(tail)].union(clusters[int(head)])
        del clusters[int(tail)]
        del clusters[int(head)]
    util.write_results_csv('findhierarchy', exp_id, 'shortest_path_tree_edges', results, fields)

def get_clusters(l):
    '''Return a dict of clusters (lists of nation ids).'''
    # There are m+1 nodes for a linkage tree with m edges
    n = l.shape[0] + 1
    clusters = dict((i, set([i])) for i in range(n))
    for i, step in enumerate(l):
        tail, head, dist, size = step
        # Stop when we reach a pre-defined threshold
        if dist > hierarchy_threshold:
            break;
        # Merge two clusters, creating a new one and deleting the originals
        clusters[n + i] = clusters[int(tail)].union(clusters[int(head)])
        del clusters[int(tail)]
        del clusters[int(head)]
    return clusters

def save_linkage(l):
    fields = ('Low', 'High', 'Dissimilarity', 'Ordinality')
    util.write_results_csv('findhierarchy', exp_id, 'video_linkage', l, fields)    
    
def save_confusion_matrix(data, l):
    '''Calculate and save a confusion matrix between video clusters and nations.'''
    num_nations = len(data.countries)
    num_videos = len(data.videos)
    # There are m+1 nodes for a linkage tree with m edges
    n = l.shape[0] + 1
    clusters = dict((i, set([i])) for i in range(n))
    cluster_len = dict((i, 1) for i in range(n))
    progress = list()
    for i, step in enumerate(np.array(l)):
        tail, head, dist, size = step
        # Stop when we have the same number of clusters as countries
        if len(clusters) <= num_nations:
            break;
        # Merge two clusters, creating a new one and deleting the originals
        clusters[n + i] = clusters[int(tail)].union(clusters[int(head)])
        old_tail = clusters[int(tail)]
        old_head = clusters[int(head)]
        del clusters[int(tail)]
        del clusters[int(head)]
        # Update length counts
        cluster_len[int(n + i)] = cluster_len[int(tail)] + cluster_len[int(head)]
        old_tail_len = cluster_len[int(tail)]
        old_head_len = cluster_len[int(head)]
        del cluster_len[int(tail)]
        del cluster_len[int(head)]
        top_len = sorted(cluster_len.values(), reverse=True)[0:num_nations]
        all_len = sorted(cluster_len.values())
        # Calculate cluster entropy
        top_total = float(sum(top_len))
        all_total = float(sum(all_len))
        top_entropy = sum([x/top_total * math.log(top_total/x,2) for x in top_len])
        all_entropy = sum([x/all_total * math.log(all_total/x,2) for x in all_len])
        progress.append((dist, all_entropy, top_entropy))
    # Find number of times each nation has trended a video in a cluster
    cluster_videos = np.zeros((num_nations, num_videos))
    vcounts = data.counts.transpose() # [vid][cid]
    best_clusters = dict(sorted(clusters.items(), key=lambda x: len(x))[-num_nations:])
    for cluster, videos in enumerate(best_clusters.itervalues()):
        for video in videos:
            cluster_videos[cluster, video] = sum(vcounts[video,:])
    # Label results
    fields = ['Id']
    for nation in range(num_nations):
        fields.append(data.country_lookup.id2tok[nation])
    results = list()
    for cluster in range(num_nations):
        result = ['Cluster %d (%d vids)' % (cluster, sum(cluster_videos[cluster,:]))]
        tail = cluster_videos[cluster,:]
        # Write individual videos
        video_results = list()
        for v in range(cluster_videos.shape[1]):
            if cluster_videos[cluster,v] > 0:
                video_results.append( (data.video_lookup.id2tok[v],) )
        util.write_results_csv(
            'findhierarchy'
            , exp_id
            , 'video_cluster_%d' % cluster
            , video_results
            , ('Id')
        )
        for nation in range(num_nations):
            head = data.counts[nation,:]
            coaffiliation = exposure.symmetric(tail, head)
            result.append(coaffiliation)
        results.append(result)
    progress_fields = ('Dissimilarity', 'Entropy', 'Top Entropy')
    util.write_results_csv('findhierarchy', exp_id, 'video_progress', progress, progress_fields)
    util.write_results_csv('findhierarchy', exp_id, 'video_confusion', results, fields)
    
if __name__ == '__main__':
    main()
