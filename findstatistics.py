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
import scipy.special as spspecial

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

# Calculate lifespan histogram
spans = range(min(spread_span.span_values), max(spread_span.span_values) + 1)
span_counts = []
for span in spans:
    span_counts.append(len([x for x in spread_span.span_values if x == span]))

# Calculate reach histogram
reaches = range(min(spread_span.spread_values), max(spread_span.spread_values) + 1)
reach_counts = []
for reach in reaches:
    reach_counts.append(len([x for x in spread_span.spread_values if x == reach]))

# Create spread/span figure
fig = plt.figure(
    figsize=(
        config.getfloat('figure', 'width_subplot_12')
        , config.getfloat('figure', 'height_subplot_12') ))

# Plot lifespan histogram
fit_shape = 2.31
ax = fig.add_subplot(121)
ax.tick_params(
    axis='both'
    , which='major'
    , labelsize=config.getint('figure', 'tick_fs') )
plt.plot(
    spans
    , np.array(span_counts) / float(len(spread_span.span_values)) 
    , '.'
    , markersize=config.getint('figure', 'marker_size')
    , markeredgewidth=0
    , markerfacecolor=config.get('figure', 'marker_color') )
y = (
        np.ones((float(len(spans)),)) 
        / spspecial.zeta(fit_shape, 1)
        / np.array(spans)**(fit_shape) )
plt.plot(spans, y, 'k-', markerfacecolor=config.get('figure', 'marker_color'))
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim([0, max(spans)])
ax.set_xlabel(
    'Source Lifespan (days)'
    , fontsize=config.getint('figure', 'axis_fs') )
ax.set_ylabel(
    'Frequency'
    , fontsize=config.getint('figure', 'axis_fs') )
ax.set_title(
    '(a) Video Source Lifespan'
    , fontsize=config.getint('figure', 'title_fs') )

# Plot lifespan histogram
fit_shape = 2.71
ax = fig.add_subplot(122)
ax.tick_params(
    axis='both'
    , which='major'
    , labelsize=config.getint('figure', 'tick_fs') )
plt.plot(
    reaches
    , np.array(reach_counts) / float(len(spread_span.spread_values)) 
    , '.'
    , markersize=config.getint('figure', 'marker_size')
    , markeredgewidth=0
    , markerfacecolor=config.get('figure', 'marker_color') )
y = (
        np.ones((float(len(reaches)),)) 
        / spspecial.zeta(fit_shape, 1)
        / np.array(reaches)**(fit_shape) )
plt.plot(reaches, y, 'k-', markerfacecolor=config.get('figure', 'marker_color'))
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlim([0, max(reaches)])
ax.set_xlabel(
    'Global Reach (nations)'
    , fontsize=config.getint('figure', 'axis_fs') )
ax.set_ylabel(
    'Frequency'
    , fontsize=config.getint('figure', 'axis_fs') )
ax.set_title(
    '(b) Video Global Reach'
    , fontsize=config.getint('figure', 'title_fs') )

# Set figure layout and save
plt.tight_layout(
    pad=config.getfloat('figure', 'pad')
    , w_pad=config.getfloat('figure', 'pad_w')
    , h_pad=config.getfloat('figure', 'pad_h') )
util.create_result_dir('findstatistics', exp_id)
fig.savefig('results/findstatistics/%s/separate-spread-span.eps' % exp_id)

# Calculate spread/span histogram
h = spread_span.spread_span_hist()
h = np.log10(h + 1)

# Create spread/span histogram figure
fig = plt.figure(
    figsize=(
        config.getfloat('figure', 'width_subplot_12')
        , config.getfloat('figure', 'height_subplot_12') ))

# Plot 2d histogram
ax = fig.add_subplot(121)
ax.tick_params(
    axis='both'
    , which='major'
    , labelsize=config.get('figure', 'tick_fs'))
xedges, yedges = spread_span.bin_edges()
x, y = np.meshgrid(xedges, yedges)
mesh = ax.pcolormesh(x, y, h.transpose(), cmap='gray', edgecolor='face')
cbticks = range(0,6)
cbar = plt.colorbar(mesh, ticks=cbticks)
cbar.solids.set_edgecolor("face")
cbar.ax.tick_params(labelsize=config.get('figure', 'tick_fs'))
cbar.set_ticklabels(['$10^{%d}$' % n for n in cbticks])
plt.draw()
ax.set_xscale('log')
ax.set_yscale('log')
ax.set_xlabel(
    'Global Reach (nations)'
    , fontsize=config.getint('figure', 'axis_fs'))
ax.set_ylabel(
    'Source Lifespan (days)'
    , fontsize=config.getint('figure', 'axis_fs'))
ax.set_title(
    '(a) Video Lifespan and Reach'
    , fontsize=config.getint('figure', 'title_fs'))
ax.set_ylim([min(yedges), max(yedges)])
ax.set_xlim([min(yedges), max(yedges)])

# Plot mean spread/span by countries
r, p = spstats.pearsonr(country_spans, country_spreads)
print 'Country mean global reach ~ Country mean source lifespan:'
print (r, p)
ax = fig.add_subplot(122)
ax.tick_params(
    axis='both'
    , which='major'
    , labelsize=config.getint('figure', 'tick_fs') )
plt.plot(
    country_spreads
    , country_spans
    , '.'
    , markersize=config.getint('figure', 'marker_size')
    , markeredgewidth=0
    , markerfacecolor=config.get('figure', 'marker_color') )
lim = max(math.ceil(max(country_spans)), math.ceil(max(country_spreads)))
ax.set_ylim([0, math.ceil(max(country_spans) + 0.5)])
ax.set_xlim([0, math.ceil(max(country_spreads) + 0.5)])
ax.set_xlabel(
    'Mean Global Reach (nations)'
    , fontsize=config.getint('figure', 'axis_fs') )
ax.set_ylabel(
    'Mean Source Lifespan (days)'
    , fontsize=config.getint('figure', 'axis_fs') )
ax.set_title(
    '(b) Mean Lifespan vs. Reach'
    , fontsize=config.getint('figure', 'title_fs') )

# Set figure layout and save
plt.tight_layout(
    pad=config.getfloat('figure', 'pad')
    , w_pad=config.getfloat('figure', 'pad_w')
    , h_pad=config.getfloat('figure', 'pad_h') )
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
spreads = list()
spans = list()
for cid in data.countries:
    spread, span = spread_span.country_mean_spread_span(cid, 'low', 'high')
    spreads.append(spread)
    spans.append(span)
print 'Low reach, high span, country mean reach ~ country mean source span:'
print spstats.pearsonr(spans, spreads)
spreads = list()
spans = list()
for cid in data.countries:
    spread, span = spread_span.country_mean_spread_span(cid, 'low', 'low')
    spreads.append(spread)
    spans.append(span)
print 'Low reach, low span, country mean reach ~ country mean source span:'
print spstats.pearsonr(spans, spreads)
spreads = list()
spans = list()
for cid in data.countries:
    spread, span = spread_span.country_mean_spread_span(cid, 'high', 'low')
    spreads.append(spread)
    spans.append(span)
print 'high reach, low span, country mean reach ~ country mean source span:'
print spstats.pearsonr(spans, spreads)
fig = plt.figure(
    figsize=(
        config.getfloat('figure', 'width_subplot_12')
        , config.getfloat('figure', 'height_subplot_12') ))
ax = fig.add_subplot(121)
ax.tick_params(
    axis='both'
    , which='major'
    , labelsize=config.getfloat('figure', 'tick_fs') )
plt.plot(
    spreads
    , spans
    , '.'
    , markeredgewidth=0
    , markerfacecolor=config.get('figure', 'marker_color')
    , markersize=config.getfloat('figure', 'marker_size') )
lim = max(math.ceil(max(spans)), math.ceil(max(spreads)))
ax.set_ylim([0, math.ceil(max(spans))])
ax.set_xlim([0, math.ceil(max(spreads))])
ax.set_xlabel(
    'Mean Global Spread (nations)'
    , fontsize=config.getfloat('figure', 'axis_fs') )
ax.set_ylabel(
    'Mean Source Lifespan (days)'
    , fontsize=config.getfloat('figure', 'axis_fs') )
ax.set_title(
    '(a) Global, short-lived trends'
    , fontsize=config.getfloat('figure', 'title_fs') )
spreads = list()
spans = list()
for cid in data.countries:
    spread, span = spread_span.country_mean_spread_span(cid, 'high', 'high')
    spreads.append(spread)
    spans.append(span)
print 'high reach, high span, country mean reach ~ country mean source span:'
print spstats.pearsonr(spans, spreads)
ax = fig.add_subplot(122)
ax.tick_params(
    axis='both'
    , which='major'
    , labelsize=config.getfloat('figure', 'tick_fs') )
plt.plot(
    spreads
    , spans
    , '.'
    , markeredgewidth=0
    , markerfacecolor=config.get('figure', 'marker_color')
    , markersize=config.getfloat('figure', 'marker_size') )
lim = max(math.ceil(max(spans)), math.ceil(max(spreads)))
ax.set_ylim([0, math.ceil(max(spans))])
ax.set_xlim([0, math.ceil(max(spreads))])
ax.set_xlabel(
    'Mean Global Spread (nations)'
    , fontsize=config.getfloat('figure', 'axis_fs') )
ax.set_ylabel(
    'Mean Source Lifespan (days)'
    , fontsize=config.getfloat('figure', 'axis_fs') )
ax.set_title(
    '(b) Global, long-lived trends'
    , fontsize=config.getfloat('figure', 'title_fs') )

# Set layout and save
plt.tight_layout(
    pad=config.getfloat('figure', 'pad')
    , w_pad=config.getfloat('figure', 'pad_w')
    , h_pad=config.getfloat('figure', 'pad_h') )
util.create_result_dir('findstatistics', exp_id)
fig.savefig('results/findstatistics/%s/country-spread-span-quad-hist.eps' % exp_id)

# Plot country mean spread vs span ratio
print 'Ratio:'
print spstats.pearsonr(country_spreads, country_span_ratios)
fig = plt.figure()
fig = plt.figure(
    figsize=(
        config.getfloat('figure', 'width_single')
        , config.getfloat('figure', 'height_single') ))
plt.plot(
    country_spreads
    , country_span_ratios
    , '.'
    , markeredgewidth=0
    , markerfacecolor=config.get('figure', 'marker_color')
    , markersize=config.getfloat('figure', 'marker_size') )
plt.xlabel(
    'Mean Global Reach (nations)'
    , fontsize=config.getfloat('figure', 'axis_fs') )
plt.ylabel(
    'Mean Lifespan Ratio'
    , fontsize=config.getfloat('figure', 'axis_fs') )
plt.title(
    'Reach vs Lifespan Ratio by Nation'
    , fontsize=config.getfloat('figure', 'title_fs') )
plt.tick_params(labelsize=config.getfloat('figure', 'tick_fs'))
plt.tight_layout(
    pad=config.getfloat('figure', 'pad')
    , w_pad=config.getfloat('figure', 'pad_w')
    , h_pad=config.getfloat('figure', 'pad_h') )
#    pad=0.25
#    , w_pad=0.75
#    , h_pad=0.75)
fig.savefig('results/findstatistics/%s/country-spread-ratio.eps' % exp_id)
