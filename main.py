import ConfigParser

import numpy as np

import geovidcorpus
import util

def main():
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    filename = 'data/%s' % config.get('data','filename')
    corpus = geovidcorpus.GeoVidCorpus.from_csv(filename)
    print "Loaded %d videos in %d countries" % corpus.corpus.shape

if __name__ == '__main__':
    main()