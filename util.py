
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
