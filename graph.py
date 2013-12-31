import networkx as nx

def weighted_in_degree_centrality(g):
    degree = dict()
    for node in g.nodes():
        degree[node] = sum([e[2]['weight'] for e in g.in_edges(node, True)])
    return degree

def weighted_out_degree_centrality(g):
    degree = dict()
    for node in g.nodes():
        degree[node] = sum([e[2]['weight'] for e in g.out_edges(node, True)])
    return degree

def weighted_degree_centrality(g):
    degree = dict()
    for node in g.nodes():
        degree[node] = sum([e[2]['weight'] for e in g.edges(node, True)])
    return degree
