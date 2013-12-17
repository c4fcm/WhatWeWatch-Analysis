import csv
import os

def write_results_csv(experiment, run, filename, data, headers):
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
    path = 'results/%s/%s/%s.csv' % (experiment, run, filename)
    with open(path, 'wb') as f:
        f.write(','.join(headers))
        f.write("\n")
        for row in data:
            f.write(','.join([str(x) for x in row]))
            f.write("\n")

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
