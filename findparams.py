from __future__ import division

import ConfigParser
import time

import numpy as np

import geovidcorpus
import lda.lda as lda
import util

exp_id = time.time()

eta_list = [0.005, 0.05, 0.5]
alpha_list = [0.001, 0.01, 0.1]
num_topics_list = [15, 20, 25, 30, 35, 40]
niter = 20
burn = 20
lag = 4

def main():
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    filename = 'data/%s' % config.get('data','filename')
    corpus = geovidcorpus.GeoVidCorpus.from_csv(filename)
    print "Loaded %d videos in %d countries" % corpus.corpus.shape
    results = list()
    for eta in eta_list:
        for alpha in alpha_list:
            for num_topics in num_topics_list:
                print "Initializing LDA model %f %f %d" % (eta, alpha, num_topics)
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
                    print '    change in log likelihood: %f' % (lik - last_lik)
                    print '    complete in %f seconds' % (time.time() - start)
                    likelihoods.append((i+1, lik, lik-last_lik))
                    last_lik = lik
                # Record parameters
                results.append(
                    (eta, alpha, num_topics, model.eta.sum()/model.eta.shape[0], model.alpha.sum()/model.alpha.shape[0], lik)
                )
                # Write topics
                topics = sorted(enumerate(model.alpha), key=lambda x: x[1], reverse=True)
                beta = model.beta()
                clusters = list()
                for k, alphak in topics:
                    countries = sorted(enumerate(beta[k,:]), key=lambda x: x[1], reverse=True)
                    for country_id, weight in countries:
                        name = corpus.countryLookup.get_token(country_id)
                        clusters.append((k, alphak, name, weight))
                filename = 'topics-%f-%f-%d' % (eta, alpha, num_topics)
                util.write_results_csv('findparams', exp_id, filename, clusters, ('topic', 'alpha_k', 'country', 'weight'))
    util.write_results_csv('findparams', exp_id, 'params', results, ('eta0', 'alpha0', 'topics', 'mean final eta', 'mean final alpha', 'likelihood'))

if __name__ == '__main__':
    main()