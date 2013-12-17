import csv
import numpy as np
import numpy.random as nprand
import util

class GeoVidCorpus(object):
    
    def __init__(self, pairs, country_lookup=None):
        '''Initialize from (country, video) tuples.'''
        countries = dict()
        videos = dict()
        for country, video in pairs:
            countries[country] = countries.get(country,0) + 1
            videos[video] = videos.get(video,0) + 1
        # Filter out videos that only trend in one country
        video_list = [v for v, i in videos.iteritems() if i > 1]
        country_list = countries.keys()
        # Create lookup tables
        self.videoLookup = util.Lookup(video_list)
        if country_lookup is None:
            self.countryLookup = util.Lookup(country_list)
        else:
            self.countryLookup = country_lookup
        # Create corpus
        self.corpus = np.zeros((len(video_list), len(country_list)), dtype='int64')
        for country, video in pairs:
            try:
                country_id = self.countryLookup.get_id(country)
                video_id = self.videoLookup.get_id(video)
                self.corpus[video_id, country_id] += 1
            except KeyError:
                pass

    @classmethod
    def from_csv(cls, filename):
        rows = list()
        with open(filename, 'rb') as f:
            reader = csv.reader(f, delimiter=',')
            # Skip header
            reader.next()
            # Parse each row
            for row in reader:
                rows.append((row[1].strip(), row[2].strip()))
        return GeoVidCorpus(rows)
    
    def subset(self, f=10.0):
        '''Create a random subset 1/f the size of this corpus.'''
        num_videos = self.corpus.shape[0]
        videos = range(num_videos)
        nprand.shuffle(videos)
        selected = list()
        for i in range(int(num_videos / f)):
            video = self.videoLookup.get_token(videos[i])
            for w, c in enumerate(self.corpus[videos[i],:]):
                country = self.countryLookup.get_token(w)
                for j in range(c):
                    selected.append((country, video))
        return GeoVidCorpus(selected)

    def cross_validation_sets(self, n=10):
        '''Create an array of (training, test) pairs.'''
        num_videos = self.corpus.shape[0]
        videos = range(num_videos)
        nprand.shuffle(videos)
        selected = list()
        size = int(num_videos / n)
        # Create partitions
        for i in range(n):
            selected.append(videos[i*size:(i+1)*size])
        # Create training and test sets
        results = list()
        for i in range(n):
            training = sum(selected[0:i], []) + sum(selected[i+1:n], [])
            test = selected[i]
            # TODO
        