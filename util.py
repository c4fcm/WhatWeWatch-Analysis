import csv
import datetime
import json
import os

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
    
    def __init__(self, filename):
        '''Load data from a csv and create useful representations'''
        # Load basic data
        self.countries = set()
        self.videos = set()
        self.dates = set()
        self.pairs = list()
        self.dates_vid_cid = {}
        self.vids_by_cid = {}
        
        # Read data file
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            # Skip header
            reader.next()
            # Load rows
            for row in reader:
                date = row[0].strip()
                loc = row[1].strip().lower()
                vid_id = row[2].strip()
                self.dates.add(date)
                self.countries.add(loc)
                self.videos.add(vid_id)
                self.pairs.append((loc, vid_id))
                self.vids_by_cid[loc] = self.vids_by_cid.get(loc, set()).union(set([vid_id]))
                # Store video dates by location by video id
                self.dates_vid_cid[vid_id] = self.dates_vid_cid.get(vid_id, dict())
                self.dates_vid_cid[vid_id][loc] = self.dates_vid_cid[vid_id].get(loc, list())
                y,m,d = date.split('-')
                self.dates_vid_cid[vid_id][loc].append(datetime.date(int(y), int(m), int(d)))
                
        # Country and video lookups
        self.country_lookup = Lookup(sorted(self.countries))
        self.video_lookup = Lookup(sorted(self.videos))
        
        # Calculate counts
        num_countries = len(self.countries)
        num_videos = len(self.videos)
        counts = np.zeros((num_countries, num_videos))
        for loc, vid_id in self.pairs:
            loc_index = self.country_lookup.get_id(loc)
            vid_index = self.video_lookup.get_id(vid_id)
            counts[loc_index][vid_index] += 1
        self.counts = counts

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
