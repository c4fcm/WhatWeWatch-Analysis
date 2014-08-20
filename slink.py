import itertools
import logging

import numpy as np
import numpy.testing as nptest
import scipy as sp
import scipy.sparse as spsparse

logger = logging.getLogger('slink')

def linkage(observations, metric):
    # Initialize data structures
    # Sibson's Pi, Lambda, M => pointers, best_distance, new_distance
    num_obs = observations.shape[0]
    pointers = np.array(range(num_obs), dtype=np.int32)
    best_distance = np.ones(num_obs) * float("inf")
    new_distance = np.zeros(num_obs)
    # Iteratively update dendrogram with each observation
    for n in itertools.count():
        # Stop if we've added all observations
        if n == num_obs:
            break
        print "Linkage progress: %d of %d = %f" % (
            n, num_obs, float(n) / float(num_obs)
        )
        logger.debug("Obs %d" % n)
        # Calculate distances from each obs to current
        head = observations[n]
        for j in itertools.count():
            if j == n:
                break
            tail = observations[j]
            new_distance[j] = metric(tail, head)
            logger.debug(" New distance %d %f" % (j, new_distance[j]))
        # Compare old best distance to new distance
        for j in itertools.count():
            if j == n:
                break
            old_head = pointers[j]
            logger.debug(" %d->%d" % (j, old_head))
            if new_distance[j] <= best_distance[j]:
                # Better, best distance of old head, and update pointer
                logger.debug(" Replacing pointer %d->%d" % (j, n))
                logger.debug("  new distance %d %f=>%f" % (
                    old_head
                    , new_distance[old_head]
                    , min(new_distance[old_head], best_distance[j])
                ))
                new_distance[old_head] = min(
                    new_distance[old_head]
                    , best_distance[j]
                )
                logger.debug("  best distance %d %f=>%f" % (
                    j, best_distance[j], new_distance[j]
                ))
                best_distance[j] = new_distance[j]
                pointers[j] = n
            else:
                # Not better, keep pointer and update new distance of head
                logger.debug(" Keeping pointer, head %d new %f=>%f" % (
                    old_head
                    , new_distance[old_head]
                    , min(new_distance[old_head], new_distance[j])
                ))
                new_distance[old_head] = min(
                    new_distance[old_head]
                    , new_distance[j]
                )
        for j in itertools.count():
            if j >= n - 1:
                break
            head = pointers[j]
            if best_distance[j] >= best_distance[head]:
                # If j joins the current observation's cluster at a lower
                # level than another cluster joins j, that cluster should
                # join the current observation's cluster instead.
                # See http://orion.lcg.ufrj.br/Dr.Dobbs/books/book5/chap16.htm
                logger.debug(" Updating pointer %d->%d" % (j, n))
                pointers[j] = n
    return (pointers, best_distance)

def pointer_to_scipy(pointers, best_distance):
    '''Convert from pointer representation to scipy representation:
    http://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html'''
    num_obs = len(pointers)
    # Initialize result structures
    results = np.zeros((num_obs - 1, 4))
    clusters = dict((x, set([x])) for x in range(num_obs))
    in_cluster = np.array(range(num_obs))
    # Sort links by ascending dissimilarity
    links = range(num_obs)
    links = sorted(links, key=lambda x:best_distance[x])
    links.pop() # Remove last (null) link
    # Iterate through links
    for j, link in enumerate(links):
        print "Conversion progress: %f" % (float(j) / float(num_obs))
        tail, head = sorted([in_cluster[link], in_cluster[pointers[link]]])
        dis = best_distance[link]
        count = len(clusters[tail]) + len(clusters[head])
        results[j, 0] = tail
        results[j, 1] = head
        results[j, 2] = dis
        results[j, 3] = count
        # Update clusters
        clusters[num_obs + j] = clusters[tail].union(clusters[head])
        del clusters[tail]
        del clusters[head]
        for obs in clusters[num_obs + j]:
            in_cluster[obs] = num_obs + j
    return results

if __name__ == '__main__':
    import unittest
    logging.basicConfig(format='%(message)s')
    #logger.setLevel(logging.DEBUG)
    
    stub_obs = np.array([5, 1, 15, 12, 7, 0])
    stub_pointers = np.array([4, 5, 3, 5, 5, 5], dtype=np.int32)
    stub_distance = np.array([2, 1, 3, 5, 4, float("inf")])
    stub_linkage = np.array([
        [1, 5, 1, 2],
        [0, 4, 2, 2],
        [2, 3, 3, 2],
        [6, 7, 4, 4],
        [8, 9, 5, 6]
    ])
    
    class SlinkTest(unittest.TestCase):
        
        def setUp(self):
            pass
        
        def test_linkage(self):
            pointers, best_distance = linkage(stub_obs, lambda x,y: abs(y - x))
            nptest.assert_allclose(pointers, stub_pointers)
            nptest.assert_allclose(best_distance, stub_distance)
            
        def test_scipy(self):
            pointers, best_distance = linkage(stub_obs, lambda x,y: abs(y - x))
            nptest.assert_allclose(pointers, stub_pointers)
            nptest.assert_allclose(best_distance, stub_distance)
            l = pointer_to_scipy(pointers, best_distance)
            nptest.assert_allclose(l, stub_linkage)
            
    unittest.main()