#!/usr/bin/env python

import sys
from lib.ngram_frequency_index import Cngram_index_enquirer

if __name__ == '__main__':
    if len(sys.argv)==1:
        print "usage: ",sys.argv[0]+' en/nl "pattern"'
        print "\tExample: "+sys.argv[0]+' en "nice *"'
        sys.exit(0)
        
    if sys.argv[1]=='en':
        folder = 'indexes/raw_hotel_reviews_en'
    elif sys.argv[1] == 'nl':
        folder = 'indexes/raw_hotel_reviews_nl'
    else:
        print "usage: ",sys.argv[0]+' en/nl "pattern"'
        print "\tExample: "+sys.argv[0]+' en "nice *"'
        sys.exit(0)
                        
        
    enquirer = Cngram_index_enquirer(folder)
    pat = sys.argv[2]
    
    items = enquirer.query(pat,False)
    for i in items[:]:
        print ' ',i
        
