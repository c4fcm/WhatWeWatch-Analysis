from __future__ import division

import ConfigParser
import csv
import datetime
import time

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
fields = ('Id', 'Mean Spread', 'Mean Span')
for loc in data.countries:
    spread = spread_span.country_mean_spread(loc)
    span = spread_span.country_mean_span(loc)
    results.append((loc, spread, span))
util.write_results_csv('findstatistics', exp_id, 'country_spread_span', results, fields)
