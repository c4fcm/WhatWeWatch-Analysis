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
for country in countries:
    dir_ex.add_node(country, name=util.country_name(country))
    sym_ex.add_node(country, name=util.country_name(country))
    sym_ex_dist.add_node(country, name=util.country_name(country))

# Add edges
n = (num_countries * (num_countries - 1)) / 2
completed = 0
last = 0
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
        sym_ex_dist.add_edge(tail, head, weight=(-np.log(ex)))
        # Print status
        completed += 1
        percent = int(100 * completed / n)
        if percent != last:
            print "%d%%" % percent
            last = percent

