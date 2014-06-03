from __future__ import division

import ConfigParser
import csv
import time

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
# Id,Label,Population
# dza,Algeria,37062820
# ...
population_filename = 'external/population-2010/population-2010.csv'

def main():
    
    # Read config
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    exp_id = str(time.time().strftime('%Y-%m-%d %H:%M:%S'))
    print 'Running findpairstats/%s' % exp_id
    
    # Read data file, save country codes and country-video pairs
    filename = 'data/%s' % config.get('data', 'filename')
    data = util.VideoData.from_csv(filename)
    
    # Plot and save migration/video exposure comparison
    stock_by_head_tail = load_migration(migration_filename)
    population = load_population(population_filename)
    fields = ('Source', 'Target', 'Video Exposure', 'Migration Exposure')
    results = find_migration(data, stock_by_head_tail, population, exp_id)
    util.write_results_csv('findmigrant', exp_id, 'migration_exposure', results, fields)

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
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            label = row[0].strip()
            total = int(row[2].strip())
            totals[label] = total
    return totals

def load_population(filename):
    population = {}
    with open(filename, 'rb') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            cid = row[0].strip()
            pop = int(row[2].strip())
            population[cid] = pop
    return population

def find_migration(data, stock_by_head_tail, population, exp_id):
    exposures = []
    mig_exposures = []
    results = []
    for tail in stock_by_head_tail.keys():
        for head in stock_by_head_tail.keys():
            # Prevent double counting
            if head >= tail:
                continue
            p_tail = population[tail]
            p_head = population[head]
            h = data.country_lookup.tok2id[head]
            t = data.country_lookup.tok2id[tail]
            ex = exposure.symmetric(data.counts[t,:], data.counts[h,:])
            to_head = stock_by_head_tail[head][tail]
            to_tail = stock_by_head_tail[tail][head]
            mig_ex = migrant_exposure_pair(to_tail, to_head, p_tail, p_head)
            exposures.append(ex)
            mig_exposures.append(mig_ex)
            results.append((tail, head, ex, mig_ex))
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
    
if __name__ == '__main__':
    main()
