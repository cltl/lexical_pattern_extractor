#!/usr/bin/env python

import sys
from lexical_pattern_extractor import Clexical_pattern_extractor

if __name__ == '__main__':
    extractor = Clexical_pattern_extractor()
    extractor.set_config(sys.argv[1])   
    extractor.set_mode('CANDIDATE')
    extractor.load_data()
    extractor.get_candidates_words()
    extractor.agglomerate_candidate_words_avg()
    extractor.save_candidates()

