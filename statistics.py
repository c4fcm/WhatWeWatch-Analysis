from __future__ import division

import numpy as np
import scipy
import scipy.stats as spstats

import util

class SpreadSpan(object):
    
    def __init__(self, data):
        '''Initialize spread/span statistics with VideoData.'''
        # Initialize statistics
        self.data = data
        self.spread_values = list()
        self.span_values = list()
        self.span_by_vid = {}
        self.spread_by_vid = {}
        
        # Calculate statistics
        for vid, dates_by_cid in data.dates_vid_cid.iteritems():
            spread = self.spread(dates_by_cid)
            span = self.span(dates_by_cid)
            self.spread_values.append(spread)
            self.span_values.append(span)
            self.span_by_vid[vid] = span
            self.spread_by_vid[vid] = spread
    
    def span(self, dates_by_cid):
        '''Lifespan of a video.'''
        dates = sorted(set.union(*[set(dates) for dates in dates_by_cid.itervalues()]), reverse=True)
        high = low = dates.pop()
        # Videos may trend multiple times
        spans = []
        while dates:
            d = dates.pop()
            days_skipped = (d - high).days - 1
            lifespan = (high - low).days + 1
            if days_skipped > max([lifespan, 6]):
                spans.append(lifespan)
                low = d
            high = d
        spans.append((high - low).days + 1)
        return float(sum(spans) / len(spans))

    def spread(self, dates_by_cid):
        return len(dates_by_cid)

    def spread_hist(self):
        results = list()
        values = self.spread_values
        counts, bins = np.histogram(values, range(1,max(values)+1))
        for i, count in enumerate(counts):
            results.append((bins[i], count / len(self.data.videos)))
        return results
    
    def span_hist(self):
        results = list()
        values = self.span_values
        counts, bins = np.histogram(values, range(1,max(values)+1))
        for i, count in enumerate(counts):
            results.append((bins[i], count / len(self.data.videos)))
        return results
    
    def mean_span(self):
        return sum(self.span_values) / len(self.span_values)
    
    def mean_spread(self):
        return sum(self.spread_values) / len(self.spread_values)
    
    def country_mean_span(self, cid):
        spans = []
        clu = self.data.country_lookup
        vlu = self.data.video_lookup
        # Count each video once for each day it trends
        for vid in self.data.vids_by_cid[cid]:
            span = self.span_by_vid[vid]
            count = self.data.counts[clu.tok2id[cid],vlu.tok2id[vid]]
            spans += [span] * count
        return sum(spans) / len(spans)
    
    def country_mean_spread(self, cid):
        spreads = []
        clu = self.data.country_lookup
        vlu = self.data.video_lookup
        # Count each video once for each day it trends
        for vid in self.data.vids_by_cid[cid]:
            spread = self.spread_by_vid[vid]
            count = self.data.counts[clu.tok2id[cid],vlu.tok2id[vid]]
            spreads += [spread] * count
        return sum(spreads) / len(spreads)
    
    def pearsonr(self):
        return spstats.pearsonr(self.spread_values, self.span_values)
