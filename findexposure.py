from __future__ import division

import ConfigParser
import csv
import sys
import time

import networkx as nx
import numpy as np

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

    # Create directed exposure, symmetric exposure, symmetric exposure distance
    print "Calculating exposure for edge weights"
    dir_ex = directed_exposure(data.counts, data.country_lookup)
    sym_ex = symmetric_exposure(data.counts, data.country_lookup)

    # Calculate centrality
    print "Calculating in-degree centrality"
    dir_ex_in_degree = graph.weighted_in_degree_centrality(dir_ex)
    nx.set_node_attributes(dir_ex, 'in-degree centrality', dir_ex_in_degree)
    
    print "Calculating out-degree centrality"
    dir_ex_out_degree = graph.weighted_out_degree_centrality(dir_ex)
    nx.set_node_attributes(dir_ex, 'out-degree centrality', dir_ex_out_degree)
    
    print "Caclulating degree centrality"
    sym_ex_degree = graph.weighted_degree_centrality(sym_ex)
    nx.set_node_attributes(sym_ex, 'undirected degree centrality', sym_ex_degree)
    
    print "Calculating right eigenvector centrality"
    dir_ex_right_eig = nx.eigenvector_centrality(dir_ex)
    nx.set_node_attributes(dir_ex, 'right eigenvector centrality', dir_ex_right_eig)
    
    print "Calculating left eigenvector centrality"
    dir_ex_left_eig = nx.eigenvector_centrality(dir_ex.reverse())
    nx.set_node_attributes(dir_ex, 'left eigenvector centrality', dir_ex_left_eig)
    
    print "Calculating symmetric eigenvector centrality"
    sym_ex_eig = nx.eigenvector_centrality(sym_ex)
    nx.set_node_attributes(sym_ex, 'undirected eigenvector centrality', sym_ex_eig)
    
    print "Calculating betweenness centrality"
    sym_ex_dist_between = nx.betweenness_centrality(sym_ex, weight='distance', normalized=False)
    nx.set_node_attributes(sym_ex, 'betweenness centrality', sym_ex_dist_between)
    
    print "Calculating recalculated betweenness centrality"
    sym_ex_dist_rebetween = recalculated_betweenness(sym_ex)
    nx.set_node_attributes(sym_ex, 'recalculated betweenness', sym_ex_dist_rebetween)
    
    # Create csv output
    rows = list()
    for country in data.countries:
        country_id = data.country_lookup.get_id(country)
        rows.append((
            country
            , util.country_name(country)
            , dir_ex.node[country_id]['in-degree centrality']
            , dir_ex.node[country_id]['out-degree centrality']
            , sym_ex.node[country_id]['undirected degree centrality']
            , dir_ex.node[country_id]['right eigenvector centrality']
            , dir_ex.node[country_id]['left eigenvector centrality']
            , sym_ex.node[country_id]['undirected eigenvector centrality']
            , sym_ex.node[country_id]['betweenness centrality']
            , sym_ex.node[country_id]['recalculated betweenness']
        ))
    
    # Write output
    fields = (
        'Code'
        , 'Name'
        , 'In-Degree Cent p(me|them)'
        , 'Out-Degree Cent p(them|me)'
        , 'Degree Cent'
        , 'Right Eig Cent (source-iness)'
        , 'Left Eig Cent (sink-iness)'
        , 'Eig Cent'
        , 'Betweenness Cent'
        , 'Recalculated Betweenness Cent')
    util.write_results_csv('findexposure', exp_id, 'countries', rows, fields)

def directed_exposure(counts, country_lookup):
    '''Calculate the directed exposure graph of a (country, video) count matrix.
    The directed exposure Aij is the expected probability over videos in
    country i that the video will also appear in country j.
    '''
    num_countries = counts.shape[0]
    num_videos = counts.shape[1]
    dir_ex = nx.DiGraph()
    # Add each country to the graphs
    for country_id in range(num_countries):
        country_code = country_lookup.get_token(country_id)
        dir_ex.add_node(country_id, name=util.country_name(country_code))
    # Add edges
    for head in range(num_countries):
        for tail in range(num_countries):
            if head == tail:
                continue
            # Calculate intersection
            in_tail = set(np.nonzero(counts[tail,:])[0].tolist())
            in_head = set(np.nonzero(counts[head,:])[0].tolist())
            in_both = list(in_head.intersection(in_tail))
            # Create a vector with 1s for videos in the intersection
            mask = np.zeros(num_videos)
            mask[in_both] = 1
            # Calculate totals
            total_tail = counts[tail,:].sum()
            # Calculate exposure (directed)
            # Expectation over videos in src of P(v in dest)
            ex = (counts[tail,:] * mask).sum() / total_tail
            dir_ex.add_edge(tail, head, weight=ex)
    return dir_ex

def symmetric_exposure(counts, country_lookup):
    '''The symmetric exposure graph of a (country, video) count matrix.
    The symmetric exposure Aij is the expectation over the union of videos in
    countries i and j that a video will be in their intersection.
    The distance -ln(Aij) is also calculated and stored as "distance".
    '''
    num_countries = counts.shape[0]
    num_videos = counts.shape[1]
    sym_ex = nx.Graph()
    
    # Add each country to the graphs
    for country_id in range(num_countries):
        country_code = country_lookup.get_token(country_id)
        sym_ex.add_node(country_id, name=util.country_name(country_code))
    # Add edges
    for head in range(num_countries):
        for tail in range(num_countries):
            # Prevent double counting of undirected edges
            if head >= tail:
                continue
            # Calculate intersection
            in_tail = set(np.nonzero(counts[tail,:])[0].tolist())
            in_head = set(np.nonzero(counts[head,:])[0].tolist())
            in_both = list(in_head.intersection(in_tail))
            # Don't add an edge if they have nothing in common
            if len(in_both) == 0:
                continue
            # Create a vector with 1s for videos in the intersection
            mask = np.zeros(num_videos)
            mask[in_both] = 1
            # Calculate totals
            total_head = counts[head,:].sum()
            total_tail = counts[tail,:].sum()
            # Calculate symmetric exposure
            ex = ((counts[tail,:] + counts[head,:]) * mask).sum() / (total_tail + total_head)
            sym_ex.add_edge(tail, head, weight=ex, distance=(-1.0*np.log(ex)))
    return sym_ex
    
    
def recalculated_betweenness(ex):
    # Copy the graph
    ex = ex.copy()
    # Calculate betweenness of full graph
    between = nx.betweenness_centrality(ex, weight='distance', normalized=False)
    # Create a copy to track the recalculated betweenness
    rebetween = between
    while len(ex.edges()) > 0:
        # Recalculate betweenness
        between = nx.betweenness_centrality(ex, weight='distance', normalized=False)
        # Store recalculated values if they're higher
        for node, value in between.iteritems():
            if value > rebetween[node]:
                rebetween[node] = value
        # Remove all edges from most central node
        node, value = sorted(between.items(), key=lambda x: x[1], reverse=True)[0]
        if (value == 0):
            # All remaining edges are trivial shortest paths
            break
        for tail, head in ex.edges(node):
            ex.remove_edge(tail, head)
        sys.stdout.write('.')
        sys.stdout.flush()
    return rebetween
    
if __name__ =='__main__':
    main()
