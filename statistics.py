from __future__ import division

import math

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
        self.span_by_cid_vid = {}
        self.median_spread_by_cid = {}
        self.median_span_by_cid = {}
        # The number of videos whose max lifespan is in a given country
        self.max_span_hist = {}
        for cid in data.countries:
            self.span_by_cid_vid[cid] = {}
            self.max_span_hist[cid] = 0
        
        # Calculate statistics
        for vid, dates_by_cid in data.dates_vid_cid.iteritems():
            spread = self.spread(dates_by_cid)
            #span = self.global_span(dates_by_cid)
            mls = self.max_local_span(dates_by_cid)
            span = mls[0][1]
            for max_cid, span in mls:
                self.max_span_hist[max_cid] += 1.0 / len(mls)
            self.spread_values.append(spread)
            self.span_values.append(span)
            self.span_by_vid[vid] = span
            self.spread_by_vid[vid] = spread
            for cid in data.countries:
                try:
                    local_span = self.local_span(dates_by_cid[cid])
                    self.span_by_cid_vid[cid][vid] = local_span
                except KeyError:
                    pass # vid didn't trend in cid
        for cid in data.countries:
            self.median_spread_by_cid[cid] = self.country_median_spread(cid)
            self.median_span_by_cid[cid] = self.country_median_spread(cid)
        self.min_spread = round(min(self.spread_values))
        self.max_spread = round(max(self.spread_values))
        self.min_span = round(min(self.span_values))
        self.max_span = round(max(self.span_values))
        self.spread_bins = self.max_spread - self.min_spread + 1
        self.span_bins = self.max_span - self.min_span + 1
    
    def local_span(self, dates):
        if len(dates) == 0:
            return 0
        spans = []
        sdates = sorted(dates, reverse=True)
        high = low = sdates.pop()
        lifespan = 1
        while sdates:
            d = sdates.pop()
            days_skipped = (d - high).days - 1
            lifespan = (high - low).days + 1
            if days_skipped > max([lifespan, 6]):
                spans.append(lifespan)
                low = d
            high = d
        spans.append(lifespan)
        return sum(spans) / len(spans)
    
    def max_local_span(self, dates_by_cid):
        spans = []
        for cid, dates in dates_by_cid.iteritems():
            sdates = sorted(dates, reverse=True)
            high = low = sdates.pop()
            lifespan = 1
            while sdates:
                d = sdates.pop()
                days_skipped = (d - high).days - 1
                lifespan = (high - low).days + 1
                if days_skipped > max([lifespan, 6]):
                    spans.append((cid, lifespan))
                    low = d
                high = d
            spans.append((cid, lifespan))
        # There may be a tie for the maximum, return all
        lifespan = max([x[1] for x in spans])
        result = [x for x in spans if x[1] == lifespan]
        return result
    
    def global_span(self, dates_by_cid):
        '''Global lifespan of a video from first to last appearance, anywhere.'''
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
        counts, bins = np.histogram(values, np.arange(0.5,max(values)+0.5))
        for i, count in enumerate(counts):
            results.append((bins[i], count / len(self.data.videos)))
        return results
    
    def span_hist(self):
        results = list()
        values = self.span_values
        counts, bins = np.histogram(values, np.arange(0.5,round(max(values))+0.5))
        for i, count in enumerate(counts):
            results.append((bins[i], count / len(self.data.videos)))
        return results
    
    def max_span(self):
        results = sorted(self.max_span_hist.items(), key=lambda x: x[1])
        return results
    
    def bin_edges(self):
        xedges = np.arange(self.min_spread - 0.5, self.max_spread + 1.5)
        yedges = np.arange(self.min_span - 0.5, self.max_span + 1.5)
        return (xedges, yedges)
    
    def spread_span_hist_country_quad(self, spread_half=None, span_half=None):
        '''Return a spread/span histogram only including videos that match the
        given quadrant for some country.'''
        xedges, yedges = self.bin_edges()
        spread_values = list()
        span_values = list()
        spread_lim = self.mean_spread()
        span_lim = self.mean_span()
        vids = self.quadrant_videos(spread_half, span_half)
        for vid, dates_by_cid in self.data.dates_vid_cid.iteritems():
            if vid in vids:
                spread = self.spread(dates_by_cid)
                mls = self.max_local_span(dates_by_cid)
                span = mls[0][1]
                spread_values.append(spread)
                span_values.append(span)
        print "By country quad: Reach: %s, Span: %s" % (spread_half, span_half)
        print spstats.pearsonr(spread_values, span_values);
        h, xe, ye = np.histogram2d(
            spread_values
            , span_values
            , [xedges, yedges]
        )
        return h
    
    def spread_span_hist(self, spread_half=None, span_half=None):
        '''Return a spread/span histogram only including videos that match the
        given quadrant over all videos.'''
        xedges, yedges = self.bin_edges()
        if spread_half == None and span_half == None:
            h, xe, ye = np.histogram2d(
                self.spread_values
                , self.span_values
                , [xedges, yedges]
            )
        else:
            spread_values = list()
            span_values = list()
            spread_lim = self.mean_spread()
            span_lim = self.mean_span()
            for vid, dates_by_cid in self.data.dates_vid_cid.iteritems():
                spread = self.spread(dates_by_cid)
                mls = self.max_local_span(dates_by_cid)
                span = mls[0][1]
                if (
                    (
                        (spread_half == 'low' and spread <= spread_lim)
                        or
                        (spread_half == 'high' and spread > spread_lim)
                    ) and (
                        (span_half == 'low' and span <= span_lim)
                        or
                        (span_half == 'high' and span > span_lim)
                    )
                ):
                    spread_values.append(spread)
                    span_values.append(span)
            print "By video quad: Reach: %s, Span: %s" % (spread_half, span_half)
            print spstats.pearsonr(spread_values, span_values);
            h, xe, ye = np.histogram2d(
                spread_values
                , span_values
                , [xedges, yedges]
            )
        return h
    
    def country_spread_span_hist(self, country):
        xedges, yedges = self.bin_edges()
        spread_values = list()
        span_values = list()
        for vid in self.data.vids_by_cid[country]:
            spread_values.append(self.spread_by_vid[vid])
            span_values.append(self.span_by_cid_vid[country][vid])
        h, xe, ye = np.histogram2d(
            spread_values
            , span_values
            , [xedges, yedges]
        )
        return h
    
    def mean_span(self):
        return sum(self.span_values) / len(self.span_values)
    
    def mean_spread(self):
        return sum(self.spread_values) / len(self.spread_values)
    
    def country_median_span(self, cid):
        spans = [self.span_by_vid[v] for v in self.data.vids_by_cid[cid]]
        spans = sorted(spans)
        return spans[int(len(spans) / 2)]
    
    def country_median_spread(self, cid):
        spread = [self.spread_by_vid[v] for v in self.data.vids_by_cid[cid]]
        spread = sorted(spread)
        return spread[int(len(spread) / 2)]
    
    def country_mean_span(self, cid, half=None):
        spans = []
        clu = self.data.country_lookup
        vlu = self.data.video_lookup
        if half != None:
            limit = self.country_mean_span(cid)[0]
        # Count each video once for each day it trends
        for vid in self.data.vids_by_cid[cid]:
            span = self.span_by_vid[vid]
            count = self.data.counts[clu.tok2id[cid],vlu.tok2id[vid]]
            if (half == None
                    or (half == 'low' and span <= limit)
                    or (half == 'high' and span > limit)):
                spans += [span] * count
        mean = sum(spans) / len(spans)
        var = sum([pow(mean - x, 2) for x in spans]) / len(spans)
        std = math.sqrt(var)
        return (mean, std)
    
    def country_mean_local_span(self, cid):
        spans = []
        clu = self.data.country_lookup
        vlu = self.data.video_lookup
        # Count each video once for each day it trends
        for vid in self.data.vids_by_cid[cid]:
            span = self.local_span(self.data.dates_vid_cid[vid][cid])
            count = self.data.counts[clu.tok2id[cid],vlu.tok2id[vid]]
            spans += [span] * count
        mean = sum(spans) / len(spans)
        var = sum([pow(mean - x, 2) for x in spans]) / len(spans)
        std = math.sqrt(var)
        return (mean, std)
    
    def country_mean_span_ratio(self, cid):
        ratios = []
        clu = self.data.country_lookup
        vlu = self.data.video_lookup
        # Count each video once for each day it trends
        for vid in self.data.vids_by_cid[cid]:
            local_span = self.local_span(self.data.dates_vid_cid[vid][cid])
            global_span = self.global_span(self.data.dates_vid_cid[vid])
            count = self.data.counts[clu.tok2id[cid],vlu.tok2id[vid]]
            ratios += [local_span / global_span] * count
        mean = sum(ratios) / len(ratios)
        var = sum([pow(mean - x, 2) for x in ratios]) / len(ratios)
        std = math.sqrt(var)
        return (mean, std)
    
    def country_mean_spread(self, cid, half=None):
        spreads = []
        clu = self.data.country_lookup
        vlu = self.data.video_lookup
        if half != None:
            limit = self.country_mean_spread(cid)[0]
        # Count each video once for each day it trends
        for vid in self.data.vids_by_cid[cid]:
            spread = self.spread_by_vid[vid]
            count = self.data.counts[clu.tok2id[cid],vlu.tok2id[vid]]
            if (half == None
                    or (half == 'low' and spread <= limit)
                    or (half == 'high' and spread > limit)):
                spreads += [spread] * count
        mean = sum(spreads) / len(spreads)
        var = sum([pow(mean - x, 2) for x in spreads]) / len(spreads)
        std = math.sqrt(var)
        return (mean, std)
    
    def country_mean_spread_span(self, cid, spread_half, span_half):
        spreads = []
        spans = []
        clu = self.data.country_lookup
        vlu = self.data.video_lookup
        spread_limit = self.country_mean_spread(cid)[0]
        span_limit = self.country_mean_span(cid)[0]
        # Count each video once for each day it trends
        for vid in self.data.vids_by_cid[cid]:
            spread = self.spread_by_vid[vid]
            span = self.span_by_vid[vid]
            count = self.data.counts[clu.tok2id[cid],vlu.tok2id[vid]]
            if (
                (
                    spread_half == 'low' and spread <= spread_limit
                    or
                    spread_half == 'high' and spread > spread_limit
                ) and (
                    span_half == 'low' and span <= span_limit
                    or
                    span_half == 'high' and span > span_limit
                )
            ):
                spreads += [spread] * count
                spans += [span] * count
        mean_spread = sum(spreads) / len(spreads)
        mean_span = sum(spans) / len(spans)
        return (mean_spread, mean_span)
    
    def quadrant_videos(self, spread_half, span_half):
        '''Return set of vids appearing in a given quadrant for some country.'''
        vids = set()
        clu = self.data.country_lookup
        vlu = self.data.video_lookup
        for cid in self.data.countries:
            spread_limit = self.country_mean_spread(cid)[0]
            span_limit = self.country_mean_span(cid)[0]
            # Count each video once for each day it trends
            for vid in self.data.vids_by_cid[cid]:
                spread = self.spread_by_vid[vid]
                span = self.span_by_vid[vid]
                count = self.data.counts[clu.tok2id[cid],vlu.tok2id[vid]]
                if (
                    (
                        spread_half == 'low' and spread <= spread_limit
                        or
                        spread_half == 'high' and spread > spread_limit
                    ) and (
                        span_half == 'low' and span <= span_limit
                        or
                        span_half == 'high' and span > span_limit
                    )
                ):
                    vids.add(vid)
        return vids
    
    def country_mean_spread_local_span(self, cid, spread_half, span_half):
        spreads = []
        spans = []
        clu = self.data.country_lookup
        vlu = self.data.video_lookup
        spread_limit = self.country_mean_spread(cid)[0]
        span_limit = self.country_mean_local_span(cid)[0]
        # Count each video once for each day it trends
        for vid in self.data.vids_by_cid[cid]:
            spread = self.spread_by_vid[vid]
            span = self.local_span(self.data.dates_vid_cid[vid][cid])
            count = self.data.counts[clu.tok2id[cid],vlu.tok2id[vid]]
            if (
                (
                    spread_half == 'low' and spread <= spread_limit
                    or
                    spread_half == 'high' and spread > spread_limit
                ) and (
                    span_half == 'low' and span <= span_limit
                    or
                    span_half == 'high' and span > span_limit
                )
            ):
                spreads += [spread] * count
                spans += [span] * count
        mean_spread = sum(spreads) / len(spreads)
        mean_span = sum(spans) / len(spans)
        return (mean_spread, mean_span)
    
    def pearsonr(self):
        return spstats.pearsonr(self.spread_values, self.span_values)
