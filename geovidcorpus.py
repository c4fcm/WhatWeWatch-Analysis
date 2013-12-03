import csv
import numpy as np
import util

class GeoVidCorpus(object):
    
    def __init__(self, pairs):
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
        self.countryLookup = util.Lookup(country_list)
        # Create corpus
        self.corpus = np.zeros((len(video_list), len(country_list)))
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
