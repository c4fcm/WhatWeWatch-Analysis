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
import external
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

# Colonial history filename
# Head, Tail
colonial_filename = 'external/colonial-2011/icow.csv'

total_migration_filename = 'external/migration-2010/total-stock.csv'
area_filename = 'external/area/area.csv'
hofstede_filename = 'external/culture/hofstede.csv'
language_diversity_filename = 'external/languages/ldi-clean.csv'
religion_filename = 'external/religion/cia-factbook.csv'
gci_filename = 'external/trade/dhl_gci_2011.csv'

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
    colonial = load_colonial(colonial_filename)
    migration = external.Migration(total_migration_filename)
    area = external.Area(area_filename)
    culture = external.Culture(hofstede_filename)
    ldi = external.Language(language_diversity_filename)
    religion = external.Religion(religion_filename)
    trade = external.Trade(gci_filename)
    fields = (
        'Source'
        , 'Target'
        , 'Video Coaff'
        , 'Pop Min', 'Pop Max', 'Pop Dense Min', 'Pop Dense Max'
        , 'GDP PC Min', 'GDP PC Max', 'GDP Max', 'GDP Min'
        , 'GCI Min', 'GCI Max'
        , 'Area Max', 'Area Min'
        , 'Dist'
        , 'Common Language', 'LDI Max', 'LDI Min'
        , 'Rel Common', 'Rel Muslim'
        , 'Col Direct'
        , 'Mig Coaff', 'Mig Total Max', 'Mig Total Min'
        , 'Inet Users Min', 'Inet Users Max', 'Inet Pen Min', 'Inet Pen Max'
        , 'PDI Max', 'PDI Min'
        , 'IDV Max', 'IDV Min'
        , 'MAS Max', 'MAS Min'
        , 'UAI Max', 'UAI Min'
        , 'LTOWVS Max', 'LTOWVS Min'
        , 'IVR Max', 'IVR Min'
    )
    results = find_pair_stats(
        data
        , migration
        , area
        , culture
        , ldi
        , religion
        , trade
        , stock_by_head_tail
        , population
        , labels
        , language
        , colonial
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

def load_colonial(data_csv):
    result = {}
    with open(data_csv, 'rU') as f:
        reader = csv.reader(f)
        #Skip header
        reader.next()
        for row in reader:
            head = row[0]
            tail = row[1]
            result[head] = result.get(head, [])
            result[head].append(tail)
            result[tail] = result.get(tail, [])
            result[tail].append(head)
    return result

def load_inet_users(filename):
    inet_users = {}
    with open(filename, 'rU') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            cid = row[0].strip().lower()
            inet_users[cid] = int(row[2].strip().lower().replace(',',''))
    return inet_users

def load_colonial(data_csv):
    result = {}
    with open(data_csv, 'rU') as f:
        reader = csv.reader(f)
        #Skip header
        reader.next()
        for row in reader:
            head = row[0]
            tail = row[1]
            result[head] = result.get(head, [])
            result[head].append(tail)
            result[tail] = result.get(tail, [])
            result[tail].append(head)
    return result

def find_pair_stats(
        data
        , migration
        , area
        , culture
        , ldi
        , religion
        , trade
        , stock_by_head_tail
        , population
        , labels
        , language
        , colonial
        , gdp
        , inet_users
        , exp_id
    ):
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
            gdp_tot_low, gdp_tot_high = sorted([gdp_head*p_head,gdp_tail*p_tail])
            # Trade
            gci_low, gci_high = sorted([trade.gci_overall[head], trade.gci_overall[tail]])
            # Area
            area_low, area_high = sorted([area.total[head], area.total[tail]])
            p_dense_head = p_head / area.total[head]
            p_dense_tail = p_tail / area.total[tail]
            p_dense_low, p_dense_high = sorted([p_dense_head, p_dense_tail])
            # Distance
            dist = distance_pair(labels[head], labels[tail])
            # Find migrant exposure
            to_head = stock_by_head_tail[head][tail]
            to_tail = stock_by_head_tail[tail][head]
            mig_ex = migrant_exposure_pair(to_head, to_tail, p_tail, p_head)
            exposures.append(ex)
            mig_exposures.append(mig_ex)
            mig_head = migration.total[head]
            mig_tail = migration.total[tail]
            mig_tot_low, mig_tot_high = sorted([mig_head/p_head, mig_tail/p_tail])
            # Language stats
            ldi_max, ldi_min = sorted([ldi.ldi[head], ldi.ldi[tail]])
            if language_common_pair(language[head], language[tail]):
                common = 1
            else:
                common = 0
            # Religion stats
            if religion.have_common(head, tail):
                religion_common = 1
            else:
                religion_common = 0
            if religion.both_are("muslim", head, tail):
                religion_muslim = 1
            else:
                religion_muslim = 0
            # Find whether there is a direct colonial relationship
            if head in colonial.get(tail, []):
                direct_colonial = 1
            else:
                direct_colonial = 0
            # Internet use stats
            inet_head = inet_users[head]
            inet_tail = inet_users[tail]
            inet_low, inet_high = sorted([inet_head, inet_tail])
            inet_low_per, inet_high_per = sorted([inet_head/p_head, inet_tail/p_tail])
            # Cultural stats
            try:
                pdi_min, pdi_max = sorted([culture.pdi[head], culture.pdi[tail]])
            except KeyError:
                pdi_min, pdi_max = ('', '')
            try:
                idv_min, idv_max = sorted([culture.idv[head], culture.idv[tail]])
            except KeyError:
                idv_min, idv_max = ('', '')
            try:
                mas_min, mas_max = sorted([culture.mas[head], culture.mas[tail]])
            except KeyError:
                mas_min, mas_max = ('', '')
            try:
                uai_min, uai_max = sorted([culture.uai[head], culture.uai[tail]])
            except KeyError:
                uai_min, uai_max = ('', '')
            try:
                ltowvs_min, ltowvs_max = sorted([culture.ltowvs[head], culture.ltowvs[tail]])            
            except KeyError:
                ltowvs_min, ltowvs_max = ('', '')
            try:
                ivr_min, ivr_max = sorted([culture.ivr[head], culture.ivr[tail]])            
            except KeyError:
                ivr_min, ivr_max = ('', '')
            # Construct result
            results.append((
                tail, head
                , ex
                , p_low, p_high, p_dense_low, p_dense_high
                , gdp_low, gdp_high, gdp_tot_low, gdp_tot_high
                , gci_low, gci_high
                , area_low, area_high
                , dist
                , common, ldi_max, ldi_min
                , religion_common, religion_muslim
                , direct_colonial
                , mig_ex
                , mig_tot_low
                , mig_tot_high
                , inet_low, inet_high, inet_low_per, inet_high_per
                , pdi_min, pdi_max
                , idv_min, idv_max
                , mas_min, mas_max
                , uai_min, uai_max
                , ltowvs_min, ltowvs_max
                , ivr_min, ivr_max
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
