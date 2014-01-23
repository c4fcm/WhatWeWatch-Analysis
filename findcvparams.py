from __future__ import division

import ConfigParser
import time

import numpy as np

import geovidcorpus
import lda.lda as lda
import util

exp_id = time.time()

eta_list = [0.1]
alpha_list = [0.001]
num_topics_list = [20]
niter = 30
burn = 20
lag = 0
cv_folds = 5

def main():
    config = ConfigParser.RawConfigParser()
    config.read('app.config')
    filename = 'data/%s' % config.get('data','filename')
    data = util.VideoData.from_csv(filename, filter_single=True)
    corpus = np.array(np.transpose(data.counts), dtype='int32')
    print "Loaded %d videos in %d countries" % corpus.shape
    results = list()
    for eta in eta_list:
        for alpha in alpha_list:
            for num_topics in num_topics_list:
                print "Running cross validation with eta=%.4f alpha=%.4f K=%d" % (eta, alpha, num_topics)
                folds = data.cross_validation_sets(cv_folds)
                perplexity = list()
                for f in range(cv_folds):
                    print "Cross validating %d/%d:" % (f, len(folds))
                    print "Initializing LDA model %f %f %d" % (eta, alpha, num_topics)
                    start = time.time()
                    fold_data = util.VideoData(folds.get_fold_training(f), proto=data)
                    test_corpus = np.array(data.rows_to_counts(folds.get_fold_test(f)).transpose(), dtype='int32')
                    model = lda.LdaModel(corpus, num_topics, alpha=alpha, eta=eta, burn=burn, lag=lag)
                    print "Initialization took %f seconds" % (time.time() - start)
                    print "Creating cross-validation folds"
                    for i in range(niter):
                        start = time.time()
                        print 'Iteration %d' % i
                        print '    doing E-step'
                        model.e_step()
                        print '    complete in %f seconds' % (time.time() - start)
                    # Record parameters
                    perplexity = model.perplexity(test_corpus)
                    results.append(
                        (eta, alpha, num_topics, model.eta.sum()/model.eta.shape[0], model.alpha.sum()/model.alpha.shape[0], perplexity)
                    )
                    # Write topics
                    topics = sorted(enumerate(model.alpha), key=lambda x: x[1], reverse=True)
                    beta = model.beta()
                    clusters = list()
                    for k, alphak in topics:
                        countries = sorted(enumerate(beta[k,:]), key=lambda x: x[1], reverse=True)
                        for country_id, weight in countries:
                            name = data.country_lookup.id2tok[country_id]
                            clusters.append((k, alphak, name, weight))
                    filename = 'topics-eta%f-alpha%f-k%d-fold%d' % (eta, alpha, num_topics, f)
                    util.write_results_csv('findcvparams', exp_id, filename, clusters, ('topic', 'alpha_k', 'country', 'weight'))
    util.write_results_csv('findcvparams', exp_id, 'params', results, ('eta0', 'alpha0', 'topics', 'mean final eta', 'mean final alpha', 'perplexity'))

if __name__ == '__main__':
    main()