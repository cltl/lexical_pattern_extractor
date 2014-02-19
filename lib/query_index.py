#!/usr/bin/env python

import sys
from ngram_frequency_index import Cngram_index_enquirer

if __name__ == '__main__':
    query = sys.argv[1]
    folder = sys.argv[2]
    enquirer = Cngram_index_enquirer(folder)
    items = enquirer.query(query)
    print 'QUERY: ',query
    print 'Top 5 results:'
    for i in items[:5]:
        print ' ',i
        
