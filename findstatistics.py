from __future__ import division

import ConfigParser
import csv
import datetime
import math
import random
import time

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as spstats

import statistics
import util

titlesize = 8
fontsize = 6
ticksize = 6

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
print "Video reach ~ Video source lifespan: %s"
print (r, p)

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
country_spread_std = list()
country_span_std = list()
country_span_ratios = list()
fields = ('Id', 'Span Ratio', 'Mean Spread', 'Spread Dev', 'Mean Global Span', 'Span Dev', 'Mean Local Span', 'Max Lifespan Count')
for loc in data.countries:
    spread, spread_std = spread_span.country_mean_spread(loc)
    span, span_std = spread_span.country_mean_span(loc)
    local_span, local_span_std = spread_span.country_mean_local_span(loc)
    max_span = spread_span.max_span_hist[loc]
    ratio, ratio_std = spread_span.country_mean_span_ratio(loc)
    country_spreads.append(spread)
    country_spans.append(span)
    country_spread_std.append(spread_std)
    country_span_std.append(span_std)
    country_span_ratios.append(ratio)
    results.append((loc, ratio, spread, spread_std, span, span_std, local_span, max_span))
util.write_results_csv('findstatistics', exp_id, 'country_spread_span', results, fields)

# Create spread/span histogram figure
fig = plt.figure(figsize=(3.3,1.5))
#fig = plt.figure(figsize=(6.6,3))

# Calculate 2d histogram
h = spread_span.spread_span_hist()
h = np.log10(h + 1)
top = max([max(x) for x in h])
cbticks = range(0,6)
ax = fig.add_subplot(121)
ax.tick_params(axis='both', which='major', labelsize=4)
xedges, yedges = spread_span.bin_edges()
x, y = np.meshgrid(xedges, yedges)
mesh = ax.pcolormesh(x, y, h.transpose(), cmap='gray', edgecolor='face')
cbar = plt.colorbar(mesh, ticks=cbticks)
cbar.solids.set_edgecolor("face")
cbar.ax.tick_params(labelsize=4)
cbar.set_ticklabels(['$10^{%d}$' % n for n in cbticks])
plt.draw()
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Global Reach (nations)', fontsize=4)
ax.set_ylabel('Source Lifespan (days)', fontsize=4)
ax.set_title('Video Lifespan vs. Reach', fontsize=6)
ax.set_ylim([min(yedges), max(yedges)])
ax.set_xlim([min(yedges), max(yedges)])

# Plot mean spread/span by countries
r, p = spstats.pearsonr(country_spans, country_spreads)
print 'Country mean global reach ~ Country mean source lifespan:'
print (r, p)
ax = fig.add_subplot(122)
ax.tick_params(axis='both', which='major', labelsize=4)
plt.plot(country_spreads, country_spans, '.', markersize=2)
lim = max(math.ceil(max(country_spans)), math.ceil(max(country_spreads)))
ax.set_ylim([0, math.ceil(max(country_spans) + 0.5)])
ax.set_xlim([0, math.ceil(max(country_spreads) + 0.5)])
ax.set_xlabel('Mean Global Reach (nations)', fontsize=4)
ax.set_ylabel('Mean Source Lifespan (days)', fontsize=4)
ax.set_title('National Mean Lifespan vs. Reach', fontsize=6)
plt.tight_layout(pad=0.25, w_pad=0.5, h_pad=0.0)
util.create_result_dir('findstatistics', exp_id)
fig.savefig('results/findstatistics/%s/spread-span-hist.eps' % exp_id)

# Calculate 2d histogram, grouped by spread/span quadrants
print "Histogramming for all videos, grouped by quadrant"
fig = plt.figure(figsize=(3.3, 3.3))
h = spread_span.spread_span_hist_country_quad('low', 'high')
h = np.log(h + 1)
ax = fig.add_subplot(221)
ax.tick_params(axis='both', which='major', labelsize=ticksize)
xedges, yedges = spread_span.bin_edges()
x, y = np.meshgrid(xedges, yedges)
ax.pcolormesh(x, y, h.transpose(), cmap='gray', edgecolor='face')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Global Spread (nations)', fontsize=fontsize)
ax.set_ylabel('Lifespan (days)', fontsize=fontsize)
ax.set_title('Video Spread/Lifespan Histogram', fontsize=titlesize)
ax.set_ylim([min(yedges), max(yedges)])
ax.set_xlim([min(yedges), max(yedges)])
h = spread_span.spread_span_hist_country_quad('high', 'high')
h = np.log(h + 1)
ax = fig.add_subplot(222)
ax.tick_params(axis='both', which='major', labelsize=ticksize)
xedges, yedges = spread_span.bin_edges()
x, y = np.meshgrid(xedges, yedges)
ax.pcolormesh(x, y, h.transpose(), cmap='gray', edgecolor='face')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Global Spread (nations)', fontsize=fontsize)
ax.set_ylabel('Lifespan (days)', fontsize=fontsize)
ax.set_title('Video Spread/Lifespan Histogram', fontsize=titlesize)
ax.set_ylim([min(yedges), max(yedges)])
ax.set_xlim([min(yedges), max(yedges)])
h = spread_span.spread_span_hist_country_quad('low', 'low')
h = np.log(h + 1)
ax = fig.add_subplot(223)
ax.tick_params(axis='both', which='major', labelsize=ticksize)
xedges, yedges = spread_span.bin_edges()
x, y = np.meshgrid(xedges, yedges)
ax.pcolormesh(x, y, h.transpose(), cmap='gray', edgecolor='face')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Global Spread (nations)', fontsize=fontsize)
ax.set_ylabel('Lifespan (days)', fontsize=fontsize)
ax.set_title('Video Spread/Lifespan Histogram', fontsize=titlesize)
ax.set_ylim([min(yedges), max(yedges)])
ax.set_xlim([min(yedges), max(yedges)])
h = spread_span.spread_span_hist_country_quad('high', 'low')
h = np.log(h + 1)
ax = fig.add_subplot(224)
ax.tick_params(axis='both', which='major', labelsize=ticksize)
xedges, yedges = spread_span.bin_edges()
x, y = np.meshgrid(xedges, yedges)
ax.pcolormesh(x, y, h.transpose(), cmap='gray', edgecolor='face')
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel('Global Spread (nations)', fontsize=fontsize)
ax.set_ylabel('Lifespan (days)', fontsize=fontsize)
ax.set_title('Video Spread/Lifespan Histogram', fontsize=titlesize)
ax.set_ylim([min(yedges), max(yedges)])
ax.set_xlim([min(yedges), max(yedges)])
util.create_result_dir('findstatistics', exp_id)
fig.savefig('results/findstatistics/%s/spread-span-quad-hist.eps' % exp_id)

# Plot mean spread/span by countries, grouping videos by spread/span quadrant
fig = plt.figure(figsize=(3.3,3.3))
spreads = list()
spans = list()
for cid in data.countries:
    spread, span = spread_span.country_mean_spread_span(cid, 'low', 'high')
    spreads.append(spread)
    spans.append(span)
ax = fig.add_subplot(221)
ax.tick_params(axis='both', which='major', labelsize=ticksize)
plt.plot(spreads, spans, '.', markersize=2)
lim = max(math.ceil(max(spans)), math.ceil(max(spreads)))
ax.set_ylim([0, math.ceil(max(spans))])
ax.set_xlim([0, math.ceil(max(spreads))])
ax.set_xlabel('Mean Global Spread (nations)', fontsize=fontsize)
ax.set_ylabel('Mean Source Lifespan (days)', fontsize=fontsize)
ax.set_title('Local, long-lived trends', fontsize=titlesize)
print 'Low reach, high span, country mean reach ~ country mean source span:'
print spstats.pearsonr(spans, spreads)
spreads = list()
spans = list()
for cid in data.countries:
    spread, span = spread_span.country_mean_spread_span(cid, 'high', 'high')
    spreads.append(spread)
    spans.append(span)
ax = fig.add_subplot(222)
ax.tick_params(axis='both', which='major', labelsize=ticksize)
plt.plot(spreads, spans, '.', markersize=2)
lim = max(math.ceil(max(spans)), math.ceil(max(spreads)))
ax.set_ylim([0, math.ceil(max(spans))])
ax.set_xlim([0, math.ceil(max(spreads))])
ax.set_xlabel('Mean Global Spread (nations)', fontsize=fontsize)
ax.set_ylabel('Mean Source Lifespan (days)', fontsize=fontsize)
ax.set_title('Global, long-lived trends', fontsize=titlesize)
print 'high reach, high span, country mean reach ~ country mean source span:'
print spstats.pearsonr(spans, spreads)
spreads = list()
spans = list()
for cid in data.countries:
    spread, span = spread_span.country_mean_spread_span(cid, 'low', 'low')
    spreads.append(spread)
    spans.append(span)
ax = fig.add_subplot(223)
ax.tick_params(axis='both', which='major', labelsize=ticksize)
plt.plot(spreads, spans, '.', markersize=2)
lim = max(math.ceil(max(spans)), math.ceil(max(spreads)))
ax.set_ylim([0, math.ceil(max(spans))])
ax.set_xlim([0, math.ceil(max(spreads))])
ax.set_xlabel('Mean Global Spread (nations)', fontsize=fontsize)
ax.set_ylabel('Mean Source Lifespan (days)', fontsize=fontsize)
ax.set_title('Local, short-lived trends', fontsize=titlesize)
print 'Low reach, low span, country mean reach ~ country mean source span:'
print spstats.pearsonr(spans, spreads)
spreads = list()
spans = list()
for cid in data.countries:
    spread, span = spread_span.country_mean_spread_span(cid, 'high', 'low')
    spreads.append(spread)
    spans.append(span)
ax = fig.add_subplot(224)
ax.tick_params(axis='both', which='major', labelsize=ticksize)
plt.plot(spreads, spans, '.', markersize=2)
lim = max(math.ceil(max(spans)), math.ceil(max(spreads)))
ax.set_ylim([0, math.ceil(max(spans))])
ax.set_xlim([0, math.ceil(max(spreads))])
ax.set_xlabel('Mean Global Spread (nations)', fontsize=fontsize)
ax.set_ylabel('Mean Source Lifespan (days)', fontsize=fontsize)
ax.set_title('Global, short-lived trends', fontsize=titlesize)
print 'high reach, low span, country mean reach ~ country mean source span:'
print spstats.pearsonr(spans, spreads)
plt.tight_layout(pad=0.25, w_pad=0.75, h_pad=0.75)
util.create_result_dir('findstatistics', exp_id)
fig.savefig('results/findstatistics/%s/country-spread-span-quad-hist.eps' % exp_id)

# Plot country mean spread vs span ratio
print 'Ratio:'
print spstats.pearsonr(country_spreads, country_span_ratios)
fig = plt.figure()
fig = plt.figure(figsize=(3.3, 2.5))
plt.plot(country_spreads, country_span_ratios, '.', markersize=2)
plt.xlabel('Mean Global Reach (nations)', fontsize=fontsize)
plt.ylabel('Mean Lifespan Ratio', fontsize=fontsize)
plt.title('Reach vs Lifespan Ratio by Nation', fontsize=titlesize)
plt.tick_params(labelsize=ticksize)
plt.tight_layout(pad=0.25, w_pad=0.75, h_pad=0.75)
fig.savefig('results/findstatistics/%s/country-spread-ratio.eps' % exp_id)
