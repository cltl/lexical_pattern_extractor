#!/usr/bin/env python

import sys
import os
import argparse

from lib.ngram_frequency_index import Cngram_index_creator


if __name__ == '__main__':

    print '2nd April 2014, moved to OPENER GITHUB ==> opinion_domain_acquisition_tools'
    sys.exit(0)
    
    this_folder = os.path.dirname(os.path.realpath(__file__))
    
    argument_parser = argparse.ArgumentParser(description='Create n-gram indexes from a set of KAF/NAF files')

    required = argument_parser.add_argument_group('Required arguments')
    input = required.add_mutually_exclusive_group(required=True)
    input.add_argument('-input_file', dest='input_file',metavar='file_with_list', help='File with a list of paths to KAF/NAF files, one per line')
    input.add_argument('-input_folder', dest='input_folder',metavar='folder', help='Folder with a set of KAF/NAF files')
    required.add_argument('-output', dest='out_folder', metavar='folder', help='Output folder to store the indexes', required=True)
    
    argument_parser.add_argument('-punc',dest='punctuation',default='.?;!', metavar='punctuation_symbols (default ".?;!")', help='Symbols to be considered as punctuation')
    argument_parser.add_argument('-no_lower', dest='lowercase', action='store_false', help='Tokens are NOT converted to lowercase (by default they are)')
    argument_parser.add_argument('-max_ngram', dest='max_ngram', type=int, default=3, metavar='integer (default 3)', help='Maximum size of n-grams to create')
    argument_parser.add_argument('-min_ngram', dest='min_ngram', type=int, default=1, metavar='integer (default 1)', help='Mininum size of n-grams to create')
    argument_parser.add_argument('-no_sent_borders', dest='sentence_delimiters',action='store_false', help='Sentence delimiters are NOT included (by default they are)')
    argument_parser.add_argument('-no_remove_out', dest='remove_output', action='store_false', help='Output folder is not removed if exists')
    argument_parser.add_argument('-min_freq', dest='min_freq', type=int, default=1, metavar='integer (default 1)', help='Minimum frequency allowed for ngram')

   
    my_args = sys.argv[1:] + ['-output','indexes/raw_hotel_reviews_nl_pos_500new','-input_file','/home/izquierdo/data/large_raw_reviews/hotel_reviews_nl.pos.500.list']
    arguments = argument_parser.parse_args(my_args)


    
    index_creator = Cngram_index_creator()
    index_creator.set_punctuation(arguments.punctuation)
    index_creator.set_convert_to_lowercase(arguments.lowercase)
    index_creator.set_max_ngram_len(arguments.max_ngram)
    index_creator.set_min_ngram_len(arguments.min_ngram)
    if arguments.input_file:
        index_creator.set_input_file_list(arguments.input_file)
    elif arguments.input_folder:
        ##TO be implemented
        pass
        
    if os.path.isabs(arguments.out_folder):
        index_creator.set_out_folder(arguments.out_folder)
    else:
        index_creator.set_out_folder(os.path.join(this_folder,arguments.out_folder))
        
    index_creator.set_include_sentence_delimiters(arguments.sentence_delimiters)
    index_creator.set_remove_out_if_exists(arguments.remove_output)
    index_creator.set_min_freq_for_ngram(arguments.min_freq)
  
    index_creator.create_ngram_index()

