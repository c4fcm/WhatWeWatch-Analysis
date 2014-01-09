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
    # Don't add an edge if they have nothing in common
    if len(in_both) == 0:
        return 0
    # Create a vector with 1s for videos in the intersection
    mask = np.zeros(len(tail))
    mask[in_both] = 1
    # Calculate symmetric exposure
    return ((tail + head) * mask).sum() / (tail.sum() + head.sum())

def distance(tail, head):
    return -1*np.log(symmetric(tail, head))

