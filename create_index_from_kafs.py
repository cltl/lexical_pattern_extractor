#!/usr/bin/env python

import sys
import os
from lib.ngram_frequency_index import Cngram_index_creator

if __name__ == '__main__':
    config_filename = sys.argv[1]
    this_folder = os.path.dirname(os.path.realpath(__file__))
    
    index_creator = Cngram_index_creator()
    index_creator.set_config(config_filename,this_folder)    
    index_creator.create_ngram_index()
    print>>sys.stderr,'All done'