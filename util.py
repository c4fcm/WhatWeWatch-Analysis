import csv
import datetime
import json
import math
import os
import random

import numpy as np

dirname = os.path.dirname(os.path.realpath(__file__))

with open(os.path.join(dirname, 'country_info.json'), 'rb') as f:
    country_list = json.loads(f.read())
country_info = dict()
for country in country_list:
    alpha3 = country['alpha-3'].lower()
    country_info[alpha3] = {
        'name': country['name']
        , 'alpha3': alpha3
    }

def country_name(alpha3):
    return country_info[alpha3]['name']

def write_results_csv(experiment, run, filename, data, headers):
    create_result_dir(experiment, run)
    path = 'results/%s/%s/%s.csv' % (experiment, run, filename)
    with open(path, 'wb') as f:
        f.write(','.join(headers))
        f.write("\n")
        for row in data:
            f.write(','.join([str(x) for x in row]))
            f.write("\n")

def create_result_dir(experiment, run):
    try:
        os.stat('results')
    except OSError:
        os.mkdir('results')
    try:
        os.stat('results/%s' % experiment)
    except OSError:
        os.mkdir('results/%s' % experiment)
    try:
        os.stat('results/%s/%s' % (experiment, run))
    except OSError:
        os.mkdir('results/%s/%s' % (experiment, run))

class VideoData(object):
    
    @classmethod
    def from_csv(cls, filename, filter_single=False):
        # Read data file
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            # Skip header and read rows
            reader.next()
            rows = []
            for row in reader:
                date = row[0].strip()
                loc = row[1].strip().lower()
                vid_id = row[2].strip()
                rows.append((date, loc, vid_id))
        return VideoData(rows, filter_single=filter_single)
    
    def __init__(self, rows, proto=None, filter_single=False):
        '''Load data from a csv and create useful representations'''
        # Load basic data
        if proto is None:
            self.countries = set()
            self.videos = set()
            self.dates = set()
            self.pairs = list()
            self.dates_vid_cid = {}
            self.vids_by_cid = {}
            self.rows_by_date = {}
            self.cids_by_vid = {}
        else:
            self.countries = proto.countries
            self.videos = proto.videos
            self.dates = set()
            self.pairs = list()
            self.dates_vid_cid = {}
            self.vids_by_cid = {}
            self.rows_by_date = {}
            self.cids_by_vid = {}
        
        # Process rows
        for row in rows:
            date = row[0]
            loc = row[1]
            vid_id = row[2]
            if proto is None:
                self.countries.add(loc)
                self.videos.add(vid_id)
            self.rows_by_date[date] = self.rows_by_date.get(date,[]) + [(date, loc, vid_id)]
            self.dates.add(date)
            self.pairs.append((loc, vid_id))
            self.vids_by_cid[loc] = self.vids_by_cid.get(loc, set()).union(set([vid_id]))
            self.cids_by_vid[vid_id] = self.cids_by_vid.get(vid_id, set()).union(set([loc]))
            # Store video dates by location by video id
            self.dates_vid_cid[vid_id] = self.dates_vid_cid.get(vid_id, dict())
            self.dates_vid_cid[vid_id][loc] = self.dates_vid_cid[vid_id].get(loc, list())
            y,m,d = date.split('-')
            self.dates_vid_cid[vid_id][loc].append(datetime.date(int(y), int(m), int(d)))
        
        exclude = set()
        if proto is None and filter_single:
            for vid, cids in self.cids_by_vid.iteritems():
                if len(cids) < 2:
                    exclude.add(vid)
        self.videos = [x for x in self.videos if not x in exclude]
        
        # Country and video lookups
        if proto is None:
            self.country_lookup = Lookup(sorted(self.countries))
            self.video_lookup = Lookup(sorted(self.videos))
        else:
            self.country_lookup = proto.country_lookup
            self.video_lookup = proto.video_lookup
        
        # Calculate counts
        num_countries = len(self.countries)
        num_videos = len(self.videos)
        print 'Creating data with %d countries and %d videos' % (num_countries, num_videos)
        counts = np.zeros((num_countries, num_videos))
        for loc, vid_id in self.pairs:
            try:
                vid_index = self.video_lookup.get_id(vid_id)
                loc_index = self.country_lookup.get_id(loc)
                counts[loc_index][vid_index] += 1
            except KeyError:
                pass
        self.counts = counts
    
    def cross_validation_sets(self, num_folds=10):
        '''Return a list of (training, test) pairs from this data set.'''
        dates = self.rows_by_date.keys()
        random.shuffle(dates)
        per_fold = int(math.floor(len(dates) / num_folds))
        folds = []
        for k in range(num_folds):
            fold = []
            for i in range(per_fold):
                date_rows = self.rows_by_date[dates.pop()]
                for row in date_rows:
                    if row[2] in self.videos:
                        fold.append(row)
            folds.append(fold)
        cv = CrossValidation()
        for k in range(num_folds):
            training = sum(folds[:k] + folds[k+1:], [])
            test = folds[k]
            cv.add_fold(training, test)
        return cv
    
    def rows_to_counts(self, rows):
        counts = np.zeros(self.counts.shape)
        for date, loc, vid_id in rows:
            v = self.video_lookup.tok2id[vid_id]
            c = self.country_lookup.tok2id[loc]
            counts[c,v] += 1
        return counts

class CrossValidation(object):
    def __init__(self):
        self.folds = []
    
    def add_fold(self, training, test):
        self.folds.append((training, test))
        
    def get_fold_training(self, i):
        return self.folds[i][0]
    
    def get_fold_test(self, i):
        return self.folds[i][1]
    
    def __len__(self):
        return len(self.folds)

class Lookup(object):
    
    def __init__(self, tokens):
        '''Create a two-way lookup between tokens and unique integer ids.'''
        self.tok2id = dict()
        self.id2tok = dict()
        next_id = 0
        for t in tokens:
            if not t in self.tok2id:
                self.tok2id[t] = next_id
                self.id2tok[next_id] = t
                next_id += 1
    
    def get_token(self, id):
        '''Get a named token from an integer id.'''
        return self.id2tok[id]
    
    def get_id(self, tok):
        '''Get an integer id for the named token.'''
        return self.tok2id[tok]
