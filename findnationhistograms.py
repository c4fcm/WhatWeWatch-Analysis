from __future__ import division

import ConfigParser
import csv
import time
import datetime

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import scipy.stats as spstats

import exposure
import statistics
import util

def main():
    
    # Read config
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    exp_id = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print 'Running findlifespanhist/%s' % exp_id
    
    # Read data file, save country codes and country-video pairs
    filename = 'data/%s' % config.get('data', 'filename')
    data = util.VideoData.from_csv(filename)
    
    # Plot and save lifespan histograms
    results = plot_spread_span_hist(data, exp_id)

def plot_span_hist(data, exp_id):
    countries = data.countries
    spread_span = statistics.SpreadSpan(data)
    for country in countries:
        spans = [spread_span.span_by_vid[vid] for vid in data.vids_by_cid[country]]
        spreads = [spread_span.spread_by_vid[vid] for vid in data.vids_by_cid[country]]
            
        # Plot
        util.create_result_dir('findexposurehist', exp_id)
        fdtitle = {'fontsize':10}
        fdaxis = {'fontsize':8}
        
        f = plt.figure(figsize=(3.3125, 3.3125))
        plt.show()
        plt.hist(spans, bins=(max(spans) - min(spans) + 1))
        hx = plt.xlabel('Video Lifespan', fontdict=fdaxis)
        hy = plt.ylabel('Count', fontdict=fdaxis)
        ht = plt.title('Lifespan Histogram (%s)' % country, fontdict=fdtitle)
        plt.tick_params('both', labelsize='7')
        plt.tight_layout()
        util.create_result_dir('findlifespanhist', exp_id)
        f.savefig('results/findlifespanhist/%s/lifespanhist-%s.eps' % (exp_id, country))

def plot_spread_span_hist(data, exp_id):
    countries = data.countries
    spread_span = statistics.SpreadSpan(data)
    for country in countries:
            
        h = spread_span.country_spread_span_hist(country)
        h = np.log(h + 1)
        f = plt.figure(figsize=(3.3125, 3.3125))
        ax = f.add_subplot(111)
        ax.tick_params(axis='both', which='major', labelsize=4)
        xedges, yedges = spread_span.bin_edges()
        x, y = np.meshgrid(xedges, yedges)
        ax.pcolormesh(x, y, h.transpose(), cmap='gray', edgecolor='face')
        ax.set_xscale('log')
        ax.set_yscale('log')
        fontsize = 10
        ax.set_xlabel('Global Spread (nations)', fontsize=fontsize)
        ax.set_ylabel('Lifespan (days)', fontsize=fontsize)
        ax.set_title('Video Spread/Lifespan Histogram: %s' % country, fontsize=fontsize)
        ax.set_ylim([min(yedges), max(yedges)])
        ax.set_xlim([min(yedges), max(yedges)])
        ax.set_aspect('equal')
        # Save
        plt.tight_layout()
        util.create_result_dir('findnationhistograms', exp_id)
        f.savefig('results/findnationhistograms/%s/spread-span-hist-%s.eps' % (exp_id, country))
    

if __name__ == '__main__':
    main()
