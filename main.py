import ConfigParser
import time

import numpy as np

import geovidcorpus
import lda.lda as lda
import util

def main():
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    filename = 'data/%s' % config.get('data','filename')
    corpus = geovidcorpus.GeoVidCorpus.from_csv(filename)
    print "Loaded %d videos in %d countries" % corpus.corpus.shape
    #subset = corpus.subset(10.0)
    subset = corpus
    print 'Subset contains %d videos' % subset.corpus.shape[0]
    print 'Subset contains %d observations' % subset.corpus.sum()
    find_clusters(subset, 50)

def find_clusters(corpus, niter=10):
    print "Initializing LDA model"
    start = time.time()
    model = lda.LdaModel(corpus.corpus, 30, alpha=0.1, eta=0.1, burn=4)
    print "Initialization took %f seconds" % (time.time() - start)
    last_lik = model.expected_log_likelihood()
    for i in range(niter):
        start = time.time()
        print 'Iteration %d' % i
        print '    doing E-step'
        model.e_step()
        print '    doing M-step'
        model.m_step()
        lik = model.expected_log_likelihood()
        print '    change in log likelihood: %f' % (lik - last_lik)
        print '    complete in %f seconds' % (time.time() - start)
        last_lik = lik
    beta = model.beta()
    for k in range(beta.shape[0]):
        print 'Topic %d' % k
        countries = sorted(enumerate(beta[k,:]), key=lambda x: x[1], reverse=True)
        for w in range(10):
            country_id, weight = countries[w]
            name = corpus.countryLookup.get_token(country_id)
            print '    %s (%f)' % (name, weight)

if __name__ == '__main__':
    main()