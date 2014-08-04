#!/usr/bin/env python

import math
import sys
from nltk.metrics import BigramAssocMeasures

'''''
http://www.nltk.org/api/nltk.metrics.html#nltk.metrics.association.NgramAssocMeasures

        w1    ~w1
     ------ ------
 w2 | n_ii | n_oi | = n_xi
     ------ ------
~w2 | n_io | n_oo |
     ------ ------
     = n_ix        TOTAL = n_xx

Parameter --> bigram_score_fn(n_ii, (n_ix, n_xi), n_xx)
'''


class Cstat_model:
    def __init__(self, n_ii,n_io,n_oi,n_oo):
        self.n_ii = n_ii
        self.n_io = n_io
        self.n_oi = n_oi
        self.n_oo = n_oo
        self.n_xi = self.n_ii + self.n_oi
        self.n_ix = self.n_ii + self.n_io
        self.n_xx = self.n_ii + self.n_oi + self.n_io + self.n_oo
        
        #self.E11 = self.R1 * self.C1 * 1.0 / self.N
        #self.E12 = self.R1 * self.C2 * 1.0 / self.N
        #self.E21 = self.R2 * self.C1 * 1.0 / self.N
        #self.E22 = self.R2 * self.C2 * 1.0 / self.N
    
    def raw_freq(self):
        return BigramAssocMeasures.raw_freq(self.n_ii,(self.n_ix, self.n_xi),self.n_xx)
        
    def chi_sq(self):
        return BigramAssocMeasures.chi_sq(self.n_ii,(self.n_ix, self.n_xi),self.n_xx)

    def dice(self):
        return BigramAssocMeasures.dice(self.n_ii,(self.n_ix, self.n_xi),self.n_xx)
    
    def fisher(self):
        return BigramAssocMeasures.fisher(self.n_ii,(self.n_ix, self.n_xi),self.n_xx)
    
    def jaccard(self):
        return BigramAssocMeasures.jaccard(self.n_ii,(self.n_ix, self.n_xi),self.n_xx)

    def likelihood_ratio(self):
        return BigramAssocMeasures.likelihood_ratio(self.n_ii,(self.n_ix, self.n_xi),self.n_xx)
    
    def mi_like(self):
        return BigramAssocMeasures.mi_like(self.n_ii,(self.n_ix, self.n_xi),self.n_xx)
    
    def pmi(self):
        return BigramAssocMeasures.pmi(self.n_ii,(self.n_ix, self.n_xi),self.n_xx)
    
    def poisson_stirling(self):
        return BigramAssocMeasures.poisson_stirling(self.n_ii,(self.n_ix, self.n_xi),self.n_xx)

    def student_t(self):
        return BigramAssocMeasures.student_t(self.n_ii,(self.n_ix, self.n_xi),self.n_xx)
    
    def apply_measure(self,type):
        try:
            if type == 'raw_freq': return self.raw_freq()
            elif type == 'chi_sq': return self.chi_sq()
            elif type == 'dice':   return self.dice()
            elif type == 'fisher': return self.fisher()
            elif type == 'jaccard': return self.jaccard()
            elif type == 'likelihood_ratio': return self.likelihood_ratio()
            elif type == 'mi_like': return self.mi_like()
            elif type == 'pmi': return self.pmi()
            elif type == 'poisson_stirling': return self.poisson_stirling()
            elif type == 'student_t': return self.student_t()
            else:
                ##Default
                return self.pmi()
        except Exception as e:
            print>>sys.stderr,'Error applying measure',type,'n_ii:',self.n_ii,'n_io:',self.n_io,'n_oi:',self.n_oi,'n_oo:',self.n_oo
            return None        
    
if __name__ == '__main__':
    #de woede
    n_ii = 474
    
    #de *
    n_io = 664386
    n_io = -474
    #* woede
    ## QUERY!! *woede - n_ii
    n_oi = 664386
    
    #* *
    n_oo = 1.32*math.pow(10,15)
    obj = Cstat_model(n_ii,n_io,n_oi,n_oo)
    print obj.apply_measure('mi_like')
    
        
        
        
