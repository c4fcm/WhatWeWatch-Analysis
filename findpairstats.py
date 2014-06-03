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
    population = load_population(population_filename)
    language = load_language(language_filename)
    fields = (
        'Source'
        , 'Target'
        , 'Video Exposure'
        , 'Common Language'
        , 'Migration Exposure'
    )
    results = find_pair_stats(
        data
        , stock_by_head_tail
        , population
        , language
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
    return population

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

def find_pair_stats(data, stock_by_head_tail, population, language, exp_id):
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
            # Find migrant exposure
            p_tail = population[tail]
            p_head = population[head]
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
            results.append((tail, head, ex, common, mig_ex))
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
    
if __name__ == '__main__':
    main()
