import numpy as np

def directed(tail, head):
    '''Expected probability that a member of tail is also a member of head.
    :param tail[n] is the number of member counts for member n.
    :param head[n] is the number of member counts for member n.
    '''
    # Calculate intersection
    in_tail = set(np.nonzero(tail)[0].tolist())
    in_head = set(np.nonzero(head)[0].tolist())
    in_both = list(in_head.intersection(in_tail))
    # Create a vector with 1s for videos in the intersection
    mask = np.zeros(len(tail))
    mask[in_both] = 1
    # Calculate exposure (directed)
    # Expectation over videos in src of P(v in dest)
    return (tail * mask).sum() / tail.sum()

def dichotomize(counts):
    '''Returns a copy of counts with all nonzero elements set to 1.'''
    d = np.zeros(counts.shape)
    d[np.nonzero(counts)] = 1.0
    return d

def mean_peers(counts):
    '''The mean number of elements sharing each member.'''
    d = dichotomize(counts)
    # Sum number of countries, subtract 1 for self country
    num_country_v = d.sum(0)
    num_peer_c = counts.dot((num_country_v - 1))
    num_vid_c = counts.sum(1)
    return num_peer_c / num_vid_c
    
def symmetric(tail, head):
    '''Expected probability that a member of the union of head and tail will
    be a member of both sets.
    :param tail[n] is the number of member counts for member n.
    :param head[n] is the number of member counts for member n.
    '''
    # Calculate intersection
    in_tail = set(np.nonzero(tail)[0].tolist())
    in_head = set(np.nonzero(head)[0].tolist())
    in_both = list(in_head.intersection(in_tail))
    if len(in_both) == 0:
        return 0
    # Don't add an edge if they have nothing in common
    if len(in_both) == 0:
        return 0
    # Create a vector with 1s for videos in the intersection
    mask = np.zeros(len(tail))
    mask[in_both] = 1
    # Calculate symmetric exposure
    return ((tail + head) * mask).sum() / (tail.sum() + head.sum())

def distance(tail, head):
    return -1*np.log2(symmetric(tail, head))

def linkage(counts):
    '''Perform hierarchical clustering and return the same structure as
    scipy.cluster.hierarchy.linkage.'''
    n, m = counts.shape
    exposure = initial_exposure(counts)
    result = np.zeros((2*n - 1, 4))
    for i in range(n - 1):
        result[i,3] = 1
    # Perform clustering
    forest = set(range(n))
    clusters = [[x] for x in range(n)]
    for i in range(n - 1):
        # Merge the pair of clusters with the highest exposure
        best = 0
        for u in forest:
            for v in forest:
                if v < u:
                    continue
                ex = exposure[u,v]
                if ex > result[n+i,2]:
                    result[n+i,0] = u
                    result[n+i,1] = v
                    result[n+i,2] = ex
                    result[n+i,3] = result[u,3] + result[v,3]
        # Remove merged clusters from forest and add new one
        u = int(result[n+i,0])
        v = int(result[n+i,1])
        forest.remove(u)
        forest.remove(v)
        forest.add(n+i)
        next = len(clusters)
        clusters.append(clusters[u] + clusters[v])
        # Calculate distance between new cluster and existing clusters
        for j in forest:
            if j != next:
                ex = cluster_exposure(clusters[next], clusters[j], exposure, counts)
                exposure[j,next] = ex
                exposure[next,j] = ex
    result = np.delete(result, range(n), 0)
    # Convert from exposure to self-information
    for i in range(n - 1):
        result[i,2] = -1*np.log2(result[i,2])
    return result

def initial_exposure(counts):
    '''Create the initial exposure array.'''
    n = counts.shape[0]
    ex = np.zeros((2*n - 1, 2*n - 1))
    for tail in range(n):
        for head in range(tail):
            d = symmetric(counts[tail,:], counts[head,:])
            ex[tail,head] = d
            ex[head,tail] = d
    return ex

def cluster_exposure(u, v, ex, counts):
    '''Calculate exposure as:
    d(u,v) = ( \sum_{i} |u[i]| max_j(d(u[i],v[j])) )
             ( \sum_{j} |v[j]| max_i(d(u[i],v[j])) )
             / (|u| + |v|)
    Where cardinalities are based on the number of videos in a country/cluster.
    '''
    nu = sum([counts[i,:].sum() for i in u])
    nv = sum([counts[j,:].sum() for j in v])
    ex_v = 0
    ex_u = 0
    for tail in v:
        ex_v += counts[tail,:].sum() * max([ex[tail,head] for head in u])
    for tail in u:
        ex_u += counts[tail,:].sum() * max([ex[tail,head] for head in v])
    return (ex_u + ex_v) / (nu + nv)
