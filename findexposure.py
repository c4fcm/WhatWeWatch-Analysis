from __future__ import division

import ConfigParser
import csv
import datetime
import sys
import time

import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import scipy.stats as spstats

import exposure
import graph
import util

# External internet use data, format is:
# Id,Label,Internet Users
# dza,Algeria,4700000
inet_users_filename = 'external/internet_users/internet_users.csv'

# External population data, format is:
# Id,Alpha2,Label,Population
# dza,dz,Algeria,37062820
# ...
population_filename = 'external/population-2010/population-2010.csv'

def main():
    # Read config
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    
    exp_id = str(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print "Beginning %s" % exp_id
    
    # Read data file, save country codes and country-video pairs
    filename = 'data/%s' % config.get('data', 'filename')
    data = util.VideoData.from_csv(filename)

    # Load population and internet penetration data
    population, labels = load_population(population_filename)
    inet_users = load_inet_users(inet_users_filename)

    # Calculate average exposure with other countries
    mean_ex = {}
    for cid in data.countries:
        mean_ex[cid] = mean_exposure(data, cid)
    mean_peers = exposure.mean_peers(data.counts)

    # Create csv wih all edge weights
    results = []
    fields = ('Source', 'Target', 'Weight')
    for tail in range(data.counts.shape[0]):
        for head in range(tail):
            ex = exposure.symmetric(data.counts[tail,:], data.counts[head,:])
            tail_cid = data.country_lookup.id2tok[tail]
            head_cid = data.country_lookup.id2tok[head]
            results.append((tail_cid, head_cid, ex))
    util.write_results_csv('findexposure', exp_id, 'all_edges', results, fields)

    # Create directed exposure, symmetric exposure, symmetric exposure distance
    print "Calculating exposure for edge weights"
    dir_ex = directed_exposure(data.counts, data.country_lookup)
    sym_ex = symmetric_exposure(data.counts, data.country_lookup)

    # Calculate centrality
    print "Calculating in-degree centrality"
    dir_ex_in_degree = graph.weighted_in_degree_centrality(dir_ex)
    nx.set_node_attributes(dir_ex, 'in-degree centrality', dir_ex_in_degree)
    
    print "Calculating out-degree centrality"
    dir_ex_out_degree = graph.weighted_out_degree_centrality(dir_ex)
    nx.set_node_attributes(dir_ex, 'out-degree centrality', dir_ex_out_degree)
    
    print "Caclulating degree centrality"
    sym_ex_degree = graph.weighted_degree_centrality(sym_ex)
    nx.set_node_attributes(sym_ex, 'undirected degree centrality', sym_ex_degree)
    
    print "Calculating right eigenvector centrality"
    dir_ex_right_eig = nx.eigenvector_centrality(dir_ex)
    nx.set_node_attributes(dir_ex, 'right eigenvector centrality', dir_ex_right_eig)
    
    print "Calculating left eigenvector centrality"
    dir_ex_left_eig = nx.eigenvector_centrality(dir_ex.reverse())
    nx.set_node_attributes(dir_ex, 'left eigenvector centrality', dir_ex_left_eig)
    
    print "Calculating symmetric eigenvector centrality"
    sym_ex_eig = nx.eigenvector_centrality(sym_ex)
    nx.set_node_attributes(sym_ex, 'undirected eigenvector centrality', sym_ex_eig)
    
    print "Calculating betweenness centrality"
    sym_ex_dist_between = nx.betweenness_centrality(sym_ex, weight='distance', normalized=False)
    nx.set_node_attributes(sym_ex, 'betweenness centrality', sym_ex_dist_between)
    
    print "Calculating recalculated betweenness centrality"
    sym_ex_dist_rebetween = recalculated_betweenness(sym_ex)
    nx.set_node_attributes(sym_ex, 'recalculated betweenness', sym_ex_dist_rebetween)
    
    # Create csv output
    rows = list()
    for country in data.countries:
        country_id = data.country_lookup.get_id(country)
        inet_pen = inet_users[country] / population[country]
        rows.append((
            country
            , util.country_name(country)
            , dir_ex.node[country_id]['in-degree centrality']
            , dir_ex.node[country_id]['out-degree centrality']
            , sym_ex.node[country_id]['undirected degree centrality']
            , dir_ex.node[country_id]['right eigenvector centrality']
            , dir_ex.node[country_id]['left eigenvector centrality']
            , sym_ex.node[country_id]['undirected eigenvector centrality']
            , sym_ex.node[country_id]['betweenness centrality']
            , sym_ex.node[country_id]['recalculated betweenness']
            , mean_ex[country]
            , mean_peers[country_id]
            , inet_pen
        ))
    
    # Write output
    fields = (
        'Id'
        , 'Label'
        , 'In-Degree Cent p(me|them)'
        , 'Out-Degree Cent p(them|me)'
        , 'Degree Centrality'
        , 'Right Eig Cent (source-iness)'
        , 'Left Eig Cent (sink-iness)'
        , 'Eigenvalue Centrality'
        , 'Betweenness Centrality'
        , 'Recalculated Betweenness Cent'
        , 'Mean Exposure'
        , 'Mean Peers'
        , 'Internet Penetration')
    util.write_results_csv('findexposure', exp_id, 'countries', rows, fields)
    
    # Plot mean co-affiliation vs eigenvalue centrality
    centrality = []
    coaffiliation = []
    for country in data.countries:
        country_id = data.country_lookup.get_id(country)
        coaffiliation.append(mean_ex[country])
        centrality.append(sym_ex.node[country_id]['undirected eigenvector centrality'])
    print 'Eigenvalue centrality ~ Mean Co-Affiliation:'
    print spstats.pearsonr(centrality, coaffiliation)
    f = plt.figure(figsize=(3.3,2.5))
    plot_centrality_coaff(centrality, coaffiliation)
    plt.show()
    plt.tight_layout(pad=0.25, w_pad=0.5, h_pad=0.0)
    util.create_result_dir('findexposure', exp_id)
    f.savefig('results/findexposure/%s/centrality-coaffiliation.eps' % (exp_id))
    

def directed_exposure(counts, country_lookup):
    '''Calculate the directed exposure graph of a (country, video) count matrix.
    The directed exposure Aij is the expected probability over videos in
    country i that the video will also appear in country j.
    '''
    num_countries = counts.shape[0]
    num_videos = counts.shape[1]
    dir_ex = nx.DiGraph()
    # Add each country to the graphs
    for country_id in range(num_countries):
        country_code = country_lookup.get_token(country_id)
        dir_ex.add_node(country_id, name=util.country_name(country_code))
    # Add edges
    for head in range(num_countries):
        for tail in range(num_countries):
            if head == tail:
                continue
            ex = exposure.directed(counts[tail], counts[head])
            if ex > 0:
                dir_ex.add_edge(tail, head, weight=ex)
    return dir_ex

def symmetric_exposure(counts, country_lookup):
    '''The symmetric exposure graph of a (country, video) count matrix.
    The symmetric exposure Aij is the expectation over the union of videos in
    countries i and j that a video will be in their intersection.
    The distance -ln(Aij) is also calculated and stored as "distance".
    '''
    num_countries = counts.shape[0]
    num_videos = counts.shape[1]
    sym_ex = nx.Graph()
    
    # Add each country to the graphs
    for country_id in range(num_countries):
        country_code = country_lookup.get_token(country_id)
        sym_ex.add_node(country_id, name=util.country_name(country_code))
    # Add edges
    for head in range(num_countries):
        for tail in range(num_countries):
            # Prevent double counting of undirected edges
            if head >= tail:
                continue
            ex = exposure.symmetric(counts[tail,:], counts[head,:])
            if (ex > 0):
                sym_ex.add_edge(tail, head, weight=ex, distance=(-1.0*np.log2(ex)))
    return sym_ex
    
    
def recalculated_betweenness(ex):
    # Copy the graph
    ex = ex.copy()
    # Calculate betweenness of full graph
    between = nx.betweenness_centrality(ex, weight='distance', normalized=False)
    # Create a copy to track the recalculated betweenness
    rebetween = between
    while len(ex.edges()) > 0:
        # Recalculate betweenness
        between = nx.betweenness_centrality(ex, weight='distance', normalized=False)
        # Store recalculated values if they're higher
        for node, value in between.iteritems():
            if value > rebetween[node]:
                rebetween[node] = value
        # Remove all edges from most central node
        node, value = sorted(between.items(), key=lambda x: x[1], reverse=True)[0]
        if (value == 0):
            # All remaining edges are trivial shortest paths
            break
        for tail, head in ex.edges(node):
            ex.remove_edge(tail, head)
        sys.stdout.write('.')
        sys.stdout.flush()
    print
    return rebetween
    
def mean_exposure(data, tail):
    '''Mean exposure of tail with all other countries.'''
    ex = 0
    tcid = data.country_lookup.tok2id[tail]
    for head in data.countries:
        if head != tail:
            hcid = data.country_lookup.tok2id[head]
            ex += exposure.symmetric(data.counts[tcid,:],data.counts[hcid,:])
    return ex / (len(data.countries) - 1)
    
def load_inet_users(filename):
    inet_users = {}
    with open(filename, 'rU') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            cid = row[0].strip().lower()
            inet_users[cid] = int(row[2].strip().lower().replace(',',''))
    return inet_users

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

def plot_centrality_coaff(centrality, coaffiliation):
    fdtitle = {'fontsize':8}
    fdaxis = {'fontsize':6}    
    plt.plot(centrality, coaffiliation, 'o')
    hx = plt.xlabel('Eigenvalue Centrality', fontdict=fdaxis)
    hy = plt.ylabel('Mean Co-Affiliation', fontdict=fdaxis)
    ht = plt.title('Mean Co-Affiliation vs. Eigenvalue Centrality', fontdict=fdtitle)
    plt.tick_params('both', labelsize='6')

if __name__ =='__main__':
    main()
