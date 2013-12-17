from __future__ import division

import ConfigParser
import time

import numpy as np

import geovidcorpus
import lda.lda as lda
import util

exp_id = time.time()

eta = 0.086
alpha = 0.001
num_topics = 20
burn = 20
lag = 4
niter = 50

def main():
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    filename = 'data/%s' % config.get('data','filename')
    corpus = geovidcorpus.GeoVidCorpus.from_csv(filename)
    print "Experiment id: %s" % exp_id
    print "Loaded %d videos in %d countries" % corpus.corpus.shape
    results = list()
    print "Initializing LDA model %f %f %d" % (alpha, eta, num_topics)
    start = time.time()
    model = lda.LdaModel(corpus.corpus, num_topics, alpha=alpha, eta=eta, burn=burn, lag=lag)
    print "Initialization took %f seconds" % (time.time() - start)
    likelihoods = list()
    last_lik = model.log_likelihood_wz()
    likelihoods.append((0, last_lik, 0))
    for i in range(niter):
        start = time.time()
        print 'Iteration %d' % i
        print '    doing E-step'
        model.e_step()
        print '    doing M-step'
        model.m_step()
        lik = model.log_likelihood_wz()
        print '    log likelihood: %f' % lik
        print '    change in log likelihood: %f' % (lik - last_lik)
        print '    complete in %f seconds' % (time.time() - start)
        likelihoods.append((i+1, lik, lik-last_lik))
        last_lik = lik
    # Write clusters
    topics = sorted(enumerate(model.alpha), key=lambda x: x[1], reverse=True)
    beta = model.beta()
    clusters = list()
    for k, alphak in topics:
        countries = sorted(enumerate(beta[k,:]), key=lambda x: x[1], reverse=True)
        for country_id, weight in countries:
            name = corpus.countryLookup.get_token(country_id)
            clusters.append((k, alphak, name, weight))
    util.write_results_csv('findclusters', exp_id, 'clusters', clusters, ('topic', 'alpha_k', 'country', 'weight'))
    util.write_results_csv('findclusters', exp_id, 'likelihood', likelihoods, ('iteration', 'likelihood', 'change'))

if __name__ == '__main__':
    main()