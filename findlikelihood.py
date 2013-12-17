import ConfigParser
import time

import numpy as np

import geovidcorpus
import lda.lda as lda
import util

exp_id = time.time()

def main():
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    filename = 'data/%s' % config.get('data','filename')
    corpus = geovidcorpus.GeoVidCorpus.from_csv(filename)
    print "Loaded %d videos in %d countries" % corpus.corpus.shape
    find_clusters(corpus, 100)

def find_clusters(corpus, niter=10):
    print "Initializing LDA model with %d videos" % corpus.corpus.shape[0]
    start = time.time()
    model = lda.LdaModel(corpus.corpus, 30, alpha=0.01, eta=0.1, burn=20, lag=4)
    print "Initialization took %f seconds" % (time.time() - start)
    likelihoods = list()
    last_lik = model.log_likelihood_wz()
    last_iter_lik = last_lik
    likelihoods.append((0, last_lik, 0))
    for i in range(niter):
        start = time.time()
        print 'Iteration %d' % i
        print '    doing E-step'
        last_lik = model.log_likelihood_wz()
        model.e_step()
        lik = model.log_likelihood_wz()
        print '        change in log likelihood: %f' % (lik - last_lik)
        print '    doing M-step'
        last_lik = lik
        model.m_step()
        lik = model.log_likelihood_wz()
        print '        change in log likelihood: %f' % (lik - last_lik)
        print '    change in log likelihood: %f' % (lik - last_iter_lik)
        print '    complete in %f seconds' % (time.time() - start)
        likelihoods.append((i+1, lik, lik-last_iter_lik))
        last_lik = lik
        last_iter_lik = lik
    beta = model.beta()
    for k in range(beta.shape[0]):
        print 'Topic %d' % k
        countries = sorted(enumerate(beta[k,:]), key=lambda x: x[1], reverse=True)
        for w in range(10):
            country_id, weight = countries[w]
            name = corpus.countryLookup.get_token(country_id)
            print '    %s (%f)' % (name, weight)
    util.write_results_csv('findlikelihood', exp_id, 'results', likelihoods, ('iteration', 'log-likelihood', 'change'))

if __name__ == '__main__':
    main()