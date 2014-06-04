from __future__ import division

import ConfigParser
import csv
import time
import datetime

import dstk
import haversine
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import scipy.stats as spstats

import exposure
import util

# External migration data, format is:
# Target,Source,Migrant Stock
# aus,arg,14190
# ...
migration_filename = 'external/migration-2010/migration_edges.csv'

# External population data, format is:
# Id,Alpha2,Label,Population
# dza,dz,Algeria,37062820
# ...
population_filename = 'external/population-2010/population-2010.csv'

# External language data, format is:
# Id,Alpha2,Label,Languages
# dza,dz,Algeria,"Arabic, French, Berber"
# ...
language_filename = 'external/languages/languages.csv'

# External GDP data, format is:
# Id,Label,GDP 2010
# DZA,Algeria,"6,907.87"
gdp_filename = 'external/gdp-2010/gdp-2010.csv'

# External internet use data, format is:
# Id,Label,Internet Users
# dza,Algeria,4700000
inet_users_filename = 'external/internet_users/internet_users.csv'

def main():
    
    # Read config
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    exp_id = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print 'Running findpairstats/%s' % exp_id
    
    # Read data file, save country codes and country-video pairs
    filename = 'data/%s' % config.get('data', 'filename')
    data = util.VideoData.from_csv(filename)
    
    # Plot and save migration/video exposure comparison
    stock_by_head_tail = load_migration(migration_filename)
    population, labels = load_population(population_filename)
    language = load_language(language_filename)
    gdp = load_gdp(gdp_filename)
    inet_users = load_inet_users(inet_users_filename)
    fields = (
        'Source'
        , 'Target'
        , 'Video Exposure'
        , 'Pop Min', 'Pop Max', 'Pop Mean', 'Pop Rel Diff'
        , 'GDP Min', 'GDP Max', 'GDP Mean', 'GDP Diff', 'GDP Rel Diff'
        , 'Distance'
        , 'Common Language'
        , 'Migration Exposure'
        , 'Inet Users Min', 'Inet Users Max', 'Inet Users Mean'
        , 'Inet Users Diff', 'Inet Users Rel Diff'
        , 'Inet Pen Min', 'Inet Pen Max', 'Inet Pen Mean'
        , 'Inet Pen Diff', 'Inet Pen Rel Diff'
    )
    results = find_pair_stats(
        data
        , stock_by_head_tail
        , population
        , labels
        , language
        , gdp
        , inet_users
        , exp_id
    )
    util.write_results_csv('findpairstats', exp_id, 'pairs', results, fields)

def load_migration(filename):
    stock_by_head_tail = {}
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            h = row[0].strip()
            t = row[1].strip()
            stock = int(row[2].strip())
            stock_by_head_tail[h] = stock_by_head_tail.get(h, {})
            stock_by_head_tail[h][t] = stock
    return stock_by_head_tail

def load_migration_totals(filename):
    totals = {}
    with open(filename, 'rU') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            label = row[0].strip()
            total = int(row[2].strip())
            totals[label] = total
    return totals

def load_population(filename):
    population = {}
    labels = {}
    with open(filename, 'rU') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            cid = row[0].strip()
            if (row[3].strip() == ''):
                pop = 0
            else:
                pop = int(row[3].strip())
            population[cid] = pop
            labels[cid] = row[2].strip()
    return population, labels

def load_language(filename):
    language = {}
    with open(filename, 'rU') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            cid = row[0].strip()
            langs = set([l.strip().lower() for l in row[3].split(',')])
            language[cid] = langs
    return language

def load_gdp(filename):
    gdp = {}
    with open(filename, 'rU') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            cid = row[0].strip().lower()
            gdp[cid] = float(row[2].strip().lower().replace(',',''))
    return gdp

def load_inet_users(filename):
    inet_users = {}
    with open(filename, 'rU') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            cid = row[0].strip().lower()
            inet_users[cid] = int(row[2].strip().lower().replace(',',''))
    return inet_users

def find_pair_stats(data, stock_by_head_tail, population, labels, language, gdp, inet_users, exp_id):
    exposures = []
    mig_exposures = []
    results = []
    for tail in stock_by_head_tail.keys():
        for head in stock_by_head_tail.keys():
            # Prevent double counting
            if head >= tail:
                continue
            # Find video exposure
            h = data.country_lookup.tok2id[head]
            t = data.country_lookup.tok2id[tail]
            ex = exposure.symmetric(data.counts[t,:], data.counts[h,:])
            # Population stats
            p_tail = population[tail]
            p_head = population[head]
            p_low = min(p_head, p_tail)
            p_high = max(p_head, p_tail)
            p_mean = (p_high + p_low) / 2.0
            p_rdiff = (p_high - p_low) / p_mean
            # GDP stats
            gdp_head = gdp[head]
            gdp_tail = gdp[tail]
            gdp_low, gdp_high = sorted([gdp_head, gdp_tail])
            gdp_mean = (gdp_low + gdp_high) / 2.0
            gdp_diff = gdp_high - gdp_low
            gdp_rdiff = gdp_diff / gdp_mean
            # Distance
            dist = distance_pair(labels[head], labels[tail])
            # Find migrant exposure
            to_head = stock_by_head_tail[head][tail]
            to_tail = stock_by_head_tail[tail][head]
            mig_ex = migrant_exposure_pair(to_head, to_tail, p_tail, p_head)
            exposures.append(ex)
            mig_exposures.append(mig_ex)
            # Find if nations share a language
            if language_common_pair(language[head], language[tail]):
                common = 1
            else:
                common = 0
            # Internet use stats
            inet_head = inet_users[head]
            inet_tail = inet_users[tail]
            inet_low, inet_high = sorted([inet_head, inet_tail])
            inet_mean = (inet_low + inet_high) / 2.0
            inet_diff = inet_high - inet_low
            inet_rdiff = inet_diff / inet_mean
            inet_low_per, inet_high_per = sorted([inet_head/p_head, inet_tail/p_tail])
            inet_mean_per = (inet_low_per + inet_high_per) / 2.0
            inet_diff_per = inet_high_per - inet_low_per
            inet_rdiff_per = inet_diff_per / inet_mean_per
            # Construct result
            results.append((
                tail, head
                , ex
                , p_low, p_high, p_mean, p_rdiff
                , gdp_low, gdp_high, gdp_mean, gdp_diff, gdp_rdiff
                , dist
                , common
                , mig_ex
                , inet_low, inet_high, inet_mean, inet_diff, inet_rdiff
                , inet_low_per, inet_high_per, inet_mean_per, inet_diff_per, inet_rdiff_per
                ))
    mig_exposures = np.array(mig_exposures)
    exposures = np.array(exposures)
    r, p = spstats.pearsonr(mig_exposures, exposures)
    print "R:%s P:%s" % (r, p)

    # Plot
    util.create_result_dir('findmigrant', exp_id)
    fdtitle = {'fontsize':10}
    fdaxis = {'fontsize':8}
    
    f = plt.figure(figsize=(3.3125, 3.3125))
    plt.show()
    plt.loglog(mig_exposures, exposures, '.')
    hx = plt.xlabel('Migrant exposure', fontdict=fdaxis)
    hy = plt.ylabel('Video exposure', fontdict=fdaxis)
    ht = plt.title('Migrant vs. video exposure', fontdict=fdtitle)
    plt.tick_params('both', labelsize='7')
    plt.ylim(0.003, 1)
    plt.tight_layout()
    f.savefig('results/findmigrant/%s/migrant-video.eps' % exp_id)

    f = plt.figure(figsize=(3.3125, 3.3125))
    plt.show()
    plt.hist(np.array(mig_exposures), 50)
    hx = plt.xlabel('Migrant exposure', fontdict=fdaxis)
    hy = plt.ylabel('Count', fontdict=fdaxis)
    ht = plt.title('Migrant exposure for all nation pairs', fontdict=fdtitle)
    plt.tick_params('both', labelsize='7')
    plt.tight_layout()
    f.savefig('results/findmigrant/%s/migrant.eps' % exp_id)

    f = plt.figure(figsize=(3.3125, 3.3125))
    plt.show()
    plt.hist(np.array(exposures), 50)
    hx = plt.xlabel('Video exposure', fontdict=fdaxis)
    hy = plt.ylabel('Count', fontdict=fdaxis)
    ht = plt.title('Video exposure for all nation pairs', fontdict=fdtitle)
    plt.tick_params('both', labelsize='7')
    plt.tight_layout()
    f.savefig('results/findmigrant/%s/video.eps' % exp_id)
    
    return results

def migrant_exposure_pair(source, target, source_pop, target_pop):
    return (target + source) / (source_pop + target_pop)

def language_common_pair(head, tail):
    return len(head.intersection(tail)) > 0

def check_place(text):
    if text == 'Slovakia':
        return 'Slovak Republic'
    if text == 'United Kingdom':
        return 'England'
    return text

def distance_pair(head, tail):
    d = dstk.DSTK()
    try:
        head_place = d.text2places(check_place(head))[0]
    except IndexError:
        print "Lookup error: %s" % head
        return 'error'
    try:
        tail_place = d.text2places(check_place(tail))[0]
    except IndexError:
        print "Lookup error: %s" % tail
        return 'error'
    head_point = (float(head_place['longitude']), float(head_place['latitude']))
    tail_point = (float(tail_place['longitude']), float(tail_place['latitude']))
    dist = haversine.haversine(head_point, tail_point)
    return dist

if __name__ == '__main__':
    main()
