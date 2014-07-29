#!/usr/bin/env python

import sys
from lib.ngram_frequency_index import Cngram_index_enquirer

if __name__ == '__main__':
    folder = 'indexes/raw_hotel_reviews_nl_pos'        
    folder = 'indexes/raw_hotel_reviews_en_pos_max4'
    enquirer = Cngram_index_enquirer(folder)
    pat = sys.argv[1]
    
    items = enquirer.query(pat,only_match=True)
    for i in items[:]:
        print ' ',i
        
