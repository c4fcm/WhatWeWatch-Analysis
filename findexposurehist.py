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
    results = find_pair_stats(data, exp_id)

def find_pair_stats(data, exp_id):
    countries = data.countries
    for country in countries:
        exposures = []
        for target in countries:
            if target == country:
                continue
            # Find video exposure
            h = data.country_lookup.tok2id[country]
            t = data.country_lookup.tok2id[target]
            exposures.append(exposure.symmetric(data.counts[t,:], data.counts[h,:]))
        # Plot
        util.create_result_dir('findexposurehist', exp_id)
        fdtitle = {'fontsize':10}
        fdaxis = {'fontsize':8}
        
        f = plt.figure(figsize=(3.3125, 3.3125))
        plt.show()
        plt.hist(exposures, bins=20)
        hx = plt.xlabel('Video Exposure', fontdict=fdaxis)
        hy = plt.ylabel('Count', fontdict=fdaxis)
        ht = plt.title('Exposure Histogram (%s)' % country, fontdict=fdtitle)
        plt.tick_params('both', labelsize='7')
        plt.tight_layout()
        f.savefig('results/findexposurehist/%s/exposurehist-%s.eps' % (exp_id, country))

if __name__ == '__main__':
    main()
