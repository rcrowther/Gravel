

class LabelGen():
    '''
    Generate data labels
    '''
    # Not for globals?
    def __init__(self):
        self.prefixes = {}

    def __call__(self, prefix):
        '''
        return 
            a new label
        '''
        if (prefix in self.prefixes):
            idx = self.prefixes[prefix]
            idx += 1
        else:
            idx = 0
        self.prefixes[prefix] = idx
        return prefix + str(idx)

    def roData(self):
        return self('ROData')
        
    def __repr__(self):
        return "LabelGen(self.prefixs:'{}')".format(self.prefixs)
        
