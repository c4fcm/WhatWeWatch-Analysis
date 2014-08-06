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
import util

def main():
    
    # Read config
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    exp_id = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print 'Running findexposurehist/%s' % exp_id
    
    # Read data file, save country codes and country-video pairs
    filename = 'data/%s' % config.get('data', 'filename')
    data = util.VideoData.from_csv(filename)
    
    # Plot and save exposure histograms
    f = plt.figure(figsize=(3.3, 1.5))
    plt.subplot('121')
    plot_edge_histogram(data, exp_id)
    plt.subplot('122')
    plot_country_histogram(data, exp_id)
    plt.show()
    plt.tight_layout(pad=0.25, w_pad=0.5, h_pad=0.0)
    util.create_result_dir('findexposurehist', exp_id)
    f.savefig('results/findexposurehist/%s/exposurehist.eps' % (exp_id))

def plot_edge_histogram(data, exp_id):
    countries = data.countries
    exposures = []
    for country in countries:
        for target in countries:
            # Find video exposure
            h = data.country_lookup.tok2id[country]
            t = data.country_lookup.tok2id[target]
            # Prevent double-counting
            if h > t:
                exposures.append(exposure.symmetric(data.counts[t,:], data.counts[h,:]))
    # Plot
    fdtitle = {'fontsize':6}
    fdaxis = {'fontsize':4}    
    plt.hist(exposures, bins=20)
    hx = plt.xlabel('Co-affiliation', fontdict=fdaxis)
    hy = plt.ylabel('Count', fontdict=fdaxis)
    ht = plt.title('Nation-Nation Co-Affiliation', fontdict=fdtitle)
    plt.tick_params('both', labelsize='4')

def plot_country_histogram(data, exp_id):
    countries = data.countries
    means = []
    for country in countries:
        exposures = []
        for target in countries:
            if target == country:
                continue
            # Find video exposure
            h = data.country_lookup.tok2id[country]
            t = data.country_lookup.tok2id[target]
            exposures.append(exposure.symmetric(data.counts[t,:], data.counts[h,:]))
        means.append(sum(exposures) / len(exposures))
    # Plot
    fdtitle = {'fontsize':6}
    fdaxis = {'fontsize':4}    
    plt.hist(exposures, bins=10)
    hx = plt.xlabel('Mean Co-affiliation', fontdict=fdaxis)
    hy = plt.ylabel('Count', fontdict=fdaxis)
    ht = plt.title('National Mean Co-Affiliation', fontdict=fdtitle)
    plt.tick_params('both', labelsize='4')

if __name__ == '__main__':
    main()
