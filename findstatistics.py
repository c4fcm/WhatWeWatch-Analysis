from __future__ import division

import ConfigParser
import csv
import datetime
import math
import time

import matplotlib.pyplot as plt;
import numpy as np

import statistics
import util

# Read config
config = ConfigParser.RawConfigParser()
config.read('app.config')

exp_id = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

videos = dict()

# Open data file
filename = 'data/%s' % config.get('data', 'filename')
data = util.VideoData.from_csv(filename)
spread_span = statistics.SpreadSpan(data)

# Find basic counts
fields = ('Videos', 'Countries', 'Dates')
counts = [(len(data.videos), len(data.countries), len(data.dates))]
util.write_results_csv('findstatistics', exp_id, 'counts', counts, fields)

# Print correlation coeff
r, p = spread_span.pearsonr()
print "Pearson R: %f" % (r)
print "p value: %f" % p

# Write video spread and lifespan to csv
results = []
for vid in data.videos:
    spread = spread_span.spread_by_vid[vid]
    span = spread_span.span_by_vid[vid]
    results.append((vid, spread, span))
util.write_results_csv('findstatistics', exp_id, 'spread_span', results, ('Video ID', 'Spread', 'Span'))

# Calculate spread histogram
spread_hist = spread_span.spread_hist()
util.write_results_csv('findstatistics', exp_id, 'spread_histogram', spread_hist, ('Spread', 'Density'))

# Calculate span histogram
span_hist = spread_span.span_hist()
util.write_results_csv('findstatistics', exp_id, 'span_histogram', span_hist, ('Span', 'Density'))

# Calculate overall mean spread/span
fields = ('Mean Spread', 'Mean Span')
results = [(spread_span.mean_spread(), spread_span.mean_span())]
util.write_results_csv('findstatistics', exp_id, 'mean_spread_span', results, fields)

# Calculate mean span/spread for each country
results = list()
country_spreads = list()
country_spans = list()
fields = ('Id', 'Mean Spread', 'Mean Span')
for loc in data.countries:
    spread = spread_span.country_mean_spread(loc)
    span = spread_span.country_mean_span(loc)
    country_spreads.append(spread)
    country_spans.append(span)
    results.append((loc, spread, span))
util.write_results_csv('findstatistics', exp_id, 'country_spread_span', results, fields)

# Calculate 2d histogram
h = spread_span.spread_span_hist()
h = np.log(h + 1)
fig = plt.figure(figsize=(7,3))
ax = fig.add_subplot(121)
xedges, yedges = spread_span.bin_edges()
x, y = np.meshgrid(xedges, yedges)
ax.pcolormesh(x, y, h.transpose(), cmap='gray')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Global Spread (nations)')
ax.set_ylabel('Lifespan (days)')
ax.set_title('Video Spread/Lifespan Histogram')
ax.set_ylim([min(yedges), max(yedges)])
ax.set_xlim([min(yedges), max(yedges)])
ax.set_aspect('equal')

# Plot mean spread/span by countries
ax = fig.add_subplot(122)
plt.plot(country_spreads, country_spans, 'o')
ax.set_ylim([0, math.ceil(max(country_spans))])
ax.set_xlim([0, math.ceil(max(country_spreads))])
ax.set_xlabel('Mean Global Spread (nations)')
ax.set_ylabel('Mean Lifespan (days)')
ax.set_title('Mean Spread/Lifespan by Nation')
plt.show()
