#!/usr/bin/env python

import sys
from lib.ngram_frequency_index import Cngram_index_enquirer

if __name__ == '__main__':
    folder = 'indexes/hotels_set1_2_en'
    folder = 'indexes/raw_hotel_reviews_en'
        
    enquirer = Cngram_index_enquirer(folder)
    pat = sys.argv[1]
    
    items = enquirer.query(pat,False)
    print pat,len(items)
    for i in items[:]:
        print ' ',i
        
    print 
#    print 'the * of *'
#    items = enquirer.query('the * of *')
#    for i in items[:10]:
#         print ' ',i
        