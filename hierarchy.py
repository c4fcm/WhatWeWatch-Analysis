
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
    count = 0;
    for i in range(n):
        for j in range(i + 1, n, 1):
            count += 1
            if count % 100 == 1:
                print "Progress: %f" % (count / result_size)
            index = (
                spmisc.comb(n, 2, exact=True)
                - spmisc.comb(n - i, 2, exact=True)
                + (j - i - 1)
            )
            tail = points[i,:]
            head = points[j,:]
            e = exposure.symmetric(tail, head)
            result[index,0] = -1 * e
    return result

def linkage(dist):
    '''Compute a hierarchical clustering linkage tree using the 'single' method
    on a condensed distance matrix represented by a sparse matrix.'''
    # Columns of linkage tree matrix
    SRC_A, SRC_B, DIST, NUM_OBS = (0, 1, 2, 3)
    # Determine number of nodes and create linkage matrix
    n = int(round((1 + math.sqrt(1 + 8*(dist.shape[0])))/2))
    l = np.zeros((n - 1, 4))
    # Create clusters
    clusters = dict((x, set([x])) for x in range(n))
    for new_index in range(n, 2*n - 1):
        keys = sorted(clusters.keys())
        for low in keys:
            for high in [key for key in keys if key > low]:
                low_points = clusters[low]
                high_points = clusters[high]
                for lp in low_points:
                    for hp in high_points:
                        d = dist[pdist_index(n, lp, hp),0] 
                        try:
                            if d < best:
                                best, best_low, best_high = d, low, high
                        except NameError:
                            best, best_low, best_high = d, low, high
        # Merge clusters
        clusters[new_index] = clusters[best_low].union(clusters[best_high])
        del clusters[best_low]
        del clusters[best_high]
        # Update linkage tree
        print "Merging %d and %d" % (best_low, best_high)
        l[new_index - n, SRC_A] = best_low
        l[new_index - n, SRC_B] = best_high
        l[new_index - n, DIST] = best
        l[new_index - n, NUM_OBS] = len(clusters[new_index])
        del best
    return l
