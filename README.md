#Lexical pattern extractor#

##Introduction##

This tool allows to generate a set of words that appear in the same contexts as a seed list that you can provide as input. The process consists of 2 steps
*1 Generation of patterns from a seed list
*2 Extraction of candidate words from the previous list of patterns

The current tool only words for Dutch, as it makes use of the Google Web 5-gram Database for Dutch, hosted in http://www.let.rug.nl/gosse/bin/Web1T5_freq.perl to
get frequencies for n-grams. It could be easily adapted to a new language or domain, providing a new source for getting ngram frequencies in that new domain/language.


##Installation##

This tools is completely developed in python, so you need python installed in your machine (recommended version 2.7). It also uses
some functionality of our python library VUA_pylib which can be found at https://github.com/cltl/VUA_pylib. You will need to clone
first this library and make sure it is on the python path or a folder where python can find it.

Then to install the tool you need to clone the github repository from:
https://github.com/cltl/lexical_pattern_extractor

Basic installation:
````
$ cd your_local_folder
$ git clone https://github.com/cltl/lexical_pattern_extractor.git
$ cd lexical_pattern_extractor
$ git clone https://github.com/cltl/VUA_pylib.git
````


##Usage of the tool##

There are 2 python scripts that perform the two tasks mentioned above:
* create_patterns.py
* generate_candidate_words.py

All the configuration options are provided on a configuration file that must follow this format:
````
[general]
output_folder = my_folder                       
seeds = toeristisch;interessante                List of ; separated seeds
ngram_len = 3                                   Length of ngrams to generate, with 5 it will use 5-grams, 4-grams, 3-grams and 2-grams
percent_selected_patterns = 25                  Percentage of first patterns sorted according to PMI to be selected
accept_patterns_with_at_least_num_seeds = 2     Minimum number of seed that a pattern must be found with to be considered as active

[google_web_query]
limit_per_query = 100                           Limit in the query for ngrams
min_freq_for_hit = 40                           Minimum frequency allowed for an n-gram
````

The options are:
* output_folder: output folder where you want to store all the generated data
* seeds: List of ; separated seeds
* ngram_len: Length of ngrams to generate, with 5 it will use 5-grams, 4-grams, 3-grams and 2-grams
* percent_selected_patterns: Percentage of first patterns sorted according to PMI to be selected
* accept_patterns_with_at_least_num_seeds: Minimum number of seed that a pattern must be found with to be considered as active
* limit_per_query: Limit in the query for ngrams
* min_freq_for_hit: Minimum frequency allowed for an n-gram

##create_patterns.py##

This script will extract the patterns, and will be stored under FOLDER(specified on config)/extracted_patterns.xml. This file will be used in the
extraction of candidate words, so it might be modified and edited before running the second part. This file is a XML file with this format:

````
patterns>
  <pattern active="1" num="0" pmi="12.5489661749">
    <value>webpagina * duitsland</value>
    <seed pmi="12.5489661749" word="toeristisch"/>
  </pattern>
  ....
````

For each extracted patter it is shown the overall PMI value (calculated from the pmi associated with each seed), if the pattern is active or not (depending
on the configuration, if it's in the first percentaga of selected patterns and if appears with the minimum number of seeds set), the value of the pattern itself
and each of the seeds that the pattern has been found with (and the pmi of this relation). To active/deactivate a pattern, the value of the "active" attribute
has be changed to 1/0. All patterns set to active (active="1") will be used later in the extraction of target words.

The create_pattern.py stores all the results of individual queries made to the web service under the folder $FOLDER/cached_result, to avoid querying the web service
more than one time for the same query. You can rerun the create_patterns.py in case of error, and if you dont remove the folder, all these cached results will be available
and the process will be faster.

##generate_candidate_words.py##

This script takes the list of active patterns from the file $FOLDER/extracted_patterns.xml and extract a set of candidate words. The final list will be shown on the screen and
stored in a CSV file with the format target_word;pmi stored in $FOLDER/extracted_words.csv


An example of usage of the tool would be:
````
$ joe my_config.cfg    
$ python create_patterns.py my_config.cfg > log.out 2> log.err &
$ joe FOLDER/extracted_patterns.xml
$ python generate_candidate_words.py my_config.cfg > log.out 2> log.err &
````




#Contact#
+ Rubén Izquierdo Beviá
+ Vrije University of Amsterdam
+ ruben.izquierdobevia@vu.nl