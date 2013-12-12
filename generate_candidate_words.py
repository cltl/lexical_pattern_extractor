#!/usr/bin/env python

import sys
from lexical_pattern_extractor import Clexical_pattern_extractor

if __name__ == '__main__':
    extractor = Clexical_pattern_extractor()
    extractor.set_config(sys.argv[1])   
    extractor.load_data()
    extractor.generate_candidate_words()
    extractor.print_to_screen()
