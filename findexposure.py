from __future__ import division

import ConfigParser
import csv
import time

import networkx as nx
import numpy as np

import util

# Read config
config = ConfigParser.RawConfigParser()
config.read('app.config')

exp_id = time.time()

# Read data file, save country codes and country-video pairs
countries = set()
videos = set()
pairs = list()
with open('data/%s' % config.get('data', 'filename'), 'rb') as f:
    reader = csv.reader(f)
    # Skip header
    reader.next()
    # Load rows
    for row in reader:
        loc = row[1].strip().lower()
        vid_id = row[2].strip()
        countries.add(loc)
        videos.add(vid_id)
        pairs.append((loc, vid_id))

# Create country and video lookups
country_lookup = util.Lookup(countries)
video_lookup = util.Lookup(videos)

# Calculate counts
num_countries = len(countries)
num_videos = len(videos)
counts = np.zeros((num_countries, num_videos))
for loc, vid_id in pairs:
    counts[country_lookup.get_id(loc)][video_lookup.get_id(vid_id)] += 1

# Create directed exposure, symmetric exposure, symmetric exposure distance 
dir_ex = nx.DiGraph()
sym_ex = nx.Graph()
sym_ex_dist = nx.Graph()

# Add each country to the graphs
for country_id in range(num_countries):
    country_code = country_lookup.get_token(country_id)
    dir_ex.add_node(country_id, name=util.country_name(country_code))
    sym_ex.add_node(country_id, name=util.country_name(country_code))
    sym_ex_dist.add_node(country_id, name=util.country_name(country_code))

# Add edges
print "Calculating exposure for edge weights"
for head in range(num_countries):
    for tail in range(num_countries):
        if head == tail:
            continue
        # Calculate intersection
        in_tail = set(np.nonzero(counts[tail,:])[0].tolist())
        in_head = set(np.nonzero(counts[head,:])[0].tolist())
        in_both = list(in_head.intersection(in_tail))
        mask = np.zeros(num_videos)
        mask[in_both] = 1
        # Calculate totals
        total_head = counts[head,:].sum()
        total_tail = counts[tail,:].sum()
        # Calculate exposure (directed)
        # Expectation over videos in src of P(v in dest)
        ex = (counts[tail,:] * mask).sum() / total_tail
        dir_ex.add_edge(tail, head, weight=ex)
        # Prevent double counting of undirected edges
        if head > tail:
            continue
        # Calculate symmetric exposure
        ex = ((counts[tail,:] + counts[head,:]) * mask).sum() / (total_tail + total_head)
        sym_ex.add_edge(tail, head, weight=ex)
        # Calculate the symmetric exposure distance
        sym_ex_dist.add_edge(tail, head, weight=(-1.0*np.log(ex)))

# Calculate centrality

print "Calculating in-degree centrality"
dir_ex_in_degree = nx.in_degree_centrality(dir_ex)
nx.set_node_attributes(dir_ex, 'in-degree centrality', dir_ex_in_degree)

print "Calculating out-degree centrality"
dir_ex_out_degree = nx.out_degree_centrality(dir_ex)
nx.set_node_attributes(dir_ex, 'out-degree centrality', dir_ex_out_degree)

print "Caclulating degree centrality"
sym_ex_degree = nx.degree_centrality(sym_ex)
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
sym_ex_dist_between = nx.betweenness_centrality(sym_ex_dist, weight='weight', normalized=False)
nx.set_node_attributes(sym_ex_dist, 'betweenness centrality', sym_ex_dist_between)

# Create csv output
rows = list()
for country in countries:
    country_id = country_lookup.get_id(country)
    rows.append((
        country
        , util.country_name(country)
        , dir_ex.node[country_id]['in-degree centrality']
        , dir_ex.node[country_id]['out-degree centrality']
        , sym_ex.node[country_id]['undirected degree centrality']
        , dir_ex.node[country_id]['right eigenvector centrality']
        , dir_ex.node[country_id]['left eigenvector centrality']
        , sym_ex.node[country_id]['undirected eigenvector centrality']
        , sym_ex_dist.node[country_id]['betweenness centrality']
    ))

# Write output
fields = (
    'Code'
    , 'Name'
    , 'In-Degree Cent'
    , 'Out-Degree Cent'
    , 'Degree Cent'
    , 'Right Eig Cent'
    , 'Left Eig Cent'
    , 'Eig Cent'
    , 'Betweenness Cent')
util.write_results_csv('findexposure', exp_id, 'countries', rows, fields)
    