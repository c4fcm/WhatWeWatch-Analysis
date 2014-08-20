
import itertools
import math
import numpy as np
import scipy as sp
import scipy.misc as spmisc

import exposure

def pdist_index(n, i, j):
    if i > j:
        i, j = (j, i)
    return (
        spmisc.comb(n, 2, exact=True)
        - spmisc.comb(n - i, 2, exact=True)
        + (j - i - 1)
    )

def pdist(points):
    '''Return a condensed distance matrix like scipy.distance.pdist but as
    an nx1 sparse matrix.'''
    n = len(points)
    result_size = spmisc.comb(n, 2, exact=True)
    print "Creating %d element sparse matrix" % result_size
    result = sp.sparse.dok_matrix((result_size, 1))
    print "Populating matrix"
    index = 0;
    for i in range(n):
        for j in range(i + 1, n, 1):
            if index % 10000 == 1:
                print "Progress: %0.4f: %d of %d" % (
                    float(index) / float(result_size)
                    , index
                    , result_size)
            tail = points[i,:]
            head = points[j,:]
            e = exposure.symmetric(tail, head)
            result[index,0] = -1 * e
            index += 1
    return result

def linkage(dist):
    '''Compute a hierarchical clustering linkage tree using the 'single' method
    on a condensed distance matrix represented by a sparse matrix.'''
    # Columns of linkage tree matrix
    SRC_A, SRC_B, DIST, NUM_OBS = (0, 1, 2, 3)
    # Determine number of nodes and create linkage matrix
    n = int(round((1 + math.sqrt(1 + 8*(dist.shape[0])))/2))
    l = np.zeros((n - 1, 4))
    m = 2*n - 1
    # Create a new distance matrix with room for clusters
    cdist = sp.sparse.dok_matrix((spmisc.comb(m, 2, exact=True),1))
    for i in range(n):
        for j in range(i+1, n):
            index = pdist_index(n, i, j)
            cindex = pdist_index(m, i, j)
            cdist[cindex,0] = dist[index, 0]
    # Create clusters
    keys = range(n)
    key_count = n
    # Loop through each iteration of the clustering algorithm
    # We use itertools.count instead of range for better performance
    for new_index in itertools.count(n):
        if new_index >= m:
            break
        print "Clustering progress: %f" % (float(new_index - n) / float(n - 1))
        for low_key_index in itertools.count():
            if low_key_index >= key_count:
                break
            for high_key_index in itertools.count(low_key_index + 1):
                if high_key_index >= key_count:
                    break
                low_key = keys[low_key_index]
                high_key = keys[high_key_index]
                d = cdist[pdist_index(m, low_key, high_key), 0]
                try:
                    if d < best:
                        best, best_low, best_high = d, low_key_index, high_key_index
                except NameError:
                    best, best_low, best_high = d, low_key_index, high_key_index
        # Remove merged clusters
        high = keys.pop(best_high)
        low = keys.pop(best_low)
        key_count -= 2
        # Add new cluster
        keys.append(new_index)
        key_count += 1
        # Update linkage tree
        l[new_index - n, SRC_A] = low
        l[new_index - n, SRC_B] = high
        l[new_index - n, DIST] = best
        if low < n:
            obs = 1
        else:
            obs = l[low - n,3]
        if high < n:
            obs += 1
        else:
            obs += l[high - n,3]
        l[new_index - n, NUM_OBS] = obs
        # Add distances to new cluster
        for ki in itertools.count():
            if ki >= key_count:
                break
            key = keys[ki]
            if key == low or key == high:
                continue
            d_low = cdist[pdist_index(m, key, low), 0]
            d_high = cdist[pdist_index(m, key, high), 0]
            pdi = pdist_index(m, key, new_index)
            cdist[pdi, 0] = min(d_low, d_high)
        # Reset for next iteration
        del best
    return l
