from __future__ import division

import ConfigParser
import csv
import datetime
import time

import numpy as np

import util

# Read config
config = ConfigParser.RawConfigParser()
config.read('app.config')

exp_id = time.time()

videos = dict()

# Open data file
all_dates = set()
all_countries = set()
all_videos = set()
by_country = {}
with open('data/%s' % config.get('data', 'filename'), 'rb') as f:
    reader = csv.reader(f)
    # Skip header
    reader.next()
    # Load rows
    for row in reader:
        date = row[0].strip()
        loc = row[1].strip()
        vid_id = row[2].strip()
        all_dates.add(date)
        all_countries.add(loc)
        all_videos.add(vid_id)
        # Store videos by country
        by_country[loc] = by_country.get(loc, []) + [vid_id]
        # Store vidoe dates by location by video id
        videos[vid_id] = videos.get(vid_id, dict())
        videos[vid_id][loc] = videos[vid_id].get(loc, list())
        y,m,d = date.split('-')
        videos[vid_id][loc].append(datetime.date(int(y), int(m), int(d)))

# Find basic counts
fields = ('Videos', 'Countries', 'Dates')
counts = [(len(all_videos), len(all_countries), len(all_dates))]
util.write_results_csv('findstatistics', exp_id, 'counts', counts, fields)

# Calculate spread and lifespan
results = list()
spread_values = list()
span_values = list()
span_lookup = {}
spread_lookup = {}
for vid_id, countries in videos.iteritems():
    # Calculate country spread
    spread = len(countries)
    spread_values.append(spread)
    # Calculate longevity span
    low = min([min(dates) for dates in countries.itervalues()])
    high = max([max(dates) for dates in countries.itervalues()])
    span = (high - low).days + 1
    span_values.append(span)
    span_lookup[vid_id] = span
    spread_lookup[vid_id] = spread
    results.append((vid_id, spread, span))
# Write results csv
util.write_results_csv('findstatistics', exp_id, 'spread_span', results, ('Video ID', 'Spread', 'Span'))

# Calculate spread histogram
spread_hist = list()
spread_counts, spread_bins = np.histogram(spread_values, range(1,max(spread_values)+1))
for i, count in enumerate(spread_counts):
    spread_hist.append((spread_bins[i], count / len(all_videos)))
util.write_results_csv('findstatistics', exp_id, 'spread_histogram', spread_hist, ('Spread', 'Density'))

# Calculate span histogram
span_hist = list()
span_counts, span_bins = np.histogram(span_values, range(1,max(span_values)+1))
for i, count in enumerate(span_counts):
    span_hist.append((span_bins[i], count / len(all_videos)))
util.write_results_csv('findstatistics', exp_id, 'span_histogram', span_hist, ('Span', 'Density'))

# Calculate overall mean spread/span
span = sum(span_values) / len(span_values)
spread = sum(spread_values) / len(spread_values)
fields = ('Mean Spread', 'Mean Span')
util.write_results_csv('findstatistics', exp_id, 'mean_spread_span', [(spread,span)], fields)

# Calculate mean span/spread for each country
results = list()
fields = ('Id', 'Mean Spread', 'Mean Span')
for loc in all_countries:
    spreads = [spread_lookup[vid] for vid in by_country[loc]]
    spans = [span_lookup[vid] for vid in by_country[loc]]
    spread = sum(spreads) / len(spreads)
    span = sum(spans) / len(spans)
    results.append((loc, spread, span))
util.write_results_csv('findstatistics', exp_id, 'country_spread_span', results, fields)

