#!/usr/bin/env python

import sys
import os
from lib.lexical_pattern_extractor import Clexical_pattern_extractor

if __name__ == '__main__':
    extractor = Clexical_pattern_extractor()
    this_folder = os.path.dirname(os.path.realpath(__file__))    
    extractor.set_config(sys.argv[1],this_folder)
    extractor.set_mode('PATTERN')
    
    extractor.create_folders()
    extractor.generate_patterns()
    extractor.agglomerate_patterns_by_avg()
    extractor.save_and_clean()