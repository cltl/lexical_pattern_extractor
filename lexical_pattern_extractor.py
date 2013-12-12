#!/usr/bin/env python

import math
import sys
import cPickle
import os
import time
from config_manager import Config_manager
from operator import itemgetter
from lxml import etree
from VUA_pylib.corpus_reader.google_web_nl import Cgoogle_web_nl, Citem



class Clexical_pattern_extractor:
    def __init__(self):
        self.my_config = Config_manager()
        self.freq_for_pattern = {}
        self.results_for_pattern = {}
        self.overall_frequency = {}

    def set_config(self,filename):
        self.my_config.set_current_folder(os.path.dirname(os.path.realpath(__file__)))
        self.my_config.set_config(filename)
        

        
    def get_ngram_len(self):
        return self.__ngram_len


    def set_ngram_len(self, value):
        self.__ngram_len = value

    def create_folders(self):
        folder = self.my_config.get_out_folder()
        if os.path.exists(folder):
            print>>sys.stderr,'Folder',folder,'already exists. Quitting...'
            #sys.exit(-1)
        else:
            os.mkdir(folder)
            os.mkdir(self.my_config.get_folder_cached_results())
            
    def query(self,pattern,fixed=None):
        ret = None
        if isinstance(pattern, list):
            pattern = ' '.join(pattern)
                
        
        name_of_stored_file = self.my_config.get_name_stored_file(pattern, self.my_config.get_min_freq(), self.my_config.get_limit_query(),fixed)
        if os.path.exists(name_of_stored_file):
            fic = open(name_of_stored_file,'rb')
            ret = cPickle.load(fic)
            fic.close()
            
            #print>>sys.stderr,'HIT !!! Loading results for ',pattern,'from cached file',name_of_stored_file
        else:
            # WE need to query the web service 
            google_web = Cgoogle_web_nl()
            google_web.set_limit(self.my_config.get_limit_query())
            google_web.set_min_freq(self.my_config.get_min_freq())
        
        
            try:
                pattern = pattern.replace('.','%')
                if fixed is None:
                    google_web.query(pattern)
                else:
                    google_web.query(pattern,fixed)
                    
                ret = google_web.get_all_items()
            except:
                print>>sys.stderr,'Exception with',pattern
                ret = []
            
            #Store the result for following usages.
            if len(ret) != 0:
                fic = open(name_of_stored_file,'wb')
                cPickle.dump(ret, fic)
                fic.close()
        
        return ret
    
    #Generates templates dor all possible ngrams 5,4,3,2..
    def generate_templates(self,word):
        templates = []
        ngram_len = self.my_config.get_ngram_len()
        for l in xrange(ngram_len,1,-1):
            
            for n in xrange(l):
                template = ['*'] * l
                template[n] = word
                templates.append(template)
        return templates
            
            
    def get_overall_frequency(self,pattern):
        if pattern in self.overall_frequency:
            t =  self.overall_frequency.get(pattern)
        else:
            res = self.query(pattern)
            t = sum(item.get_hits() for item in res)
            self.overall_frequency[pattern] = t
        return t
            
            
            
    def get_frequency_for_word(self,target):
        r = self.query(target)
        if len(r)==0:
            return 0
        else:
            return r[0].get_hits()
        
    def calculate_total_freq(self,results):
        t = 0
        for item in results:
            t += item.get_hits()
        return t
        
    def replace_word(self,target_word,pattern):
        return pattern.replace(target_word,'*')
        
            
    def get_patterns_for_seed(self,seed):
        # Processing one target, or seed
        
        # Get the frequency of the target
        print>>sys.stderr,'Creating patterns for seed:',seed
        freq_target = self.get_overall_frequency(seed)
        
        # Get all the patterns+seed where the seed appears
        # interessante informatie over
        # interessante A B
        results_per_template = []
        templates = self.generate_templates(seed)
        total = 0
        for n,template in enumerate(templates):
            # Template is like interessante * *
            print>>sys.stderr,'  Querying google with: ',template
            results = self.query(template)
            print>>sys.stderr,'  Results obtained: ',len(results)
            total += len(results)
            results_per_template.append((template,results))
            

        # For each set of results    
        cnt = 0    
        for template, results in results_per_template:
            for item in results:
                print>>sys.stderr,'  Item number ',cnt,'of',total
                cnt += 1
                # Item could be --> interessante producten en
                pattern_with_seed = item.get_word()    
                freq_pattern_with_seed = item.get_hits()
                print>>sys.stderr,'    Pattern+seed:',pattern_with_seed
                print>>sys.stderr,'    Freq pattern+seed',freq_pattern_with_seed  
                # Get the general pattern, from interessante producten en
                # would get * producten en 
                pattern = self.replace_word(seed, pattern_with_seed)
                
                freq_pattern = self.get_overall_frequency(pattern)
                #results_for_new_pattern = self.query(pattern)
                #freq_pattern = self.calculate_total_freq(results_for_new_pattern)
               
                print>>sys.stderr,'    Pattern:',pattern
                print>>sys.stderr,'    Freq pattern',freq_pattern
                
                pmi = self.pmi(freq_pattern_with_seed,freq_target,freq_pattern)
                
                if pmi is not None:
                    if pattern in self.results_for_pattern:
                        self.results_for_pattern[pattern].append((seed,pmi))    #GLOBAL VARIABLE
                    else:
                        self.results_for_pattern[pattern] = [(seed,pmi)]
                    print>>sys.stderr,'    PMI:',pmi
        del results_per_template


    
    # Calculate PMI between SEED and PATTERN (pmi or whateveR)
    #N = math.pow(10,18) # one trillion 10^18
    # Simplified value
    # 1) log(A * B) = log A + log B
    # 2) log 10^n = n        
    def pmi(self,freq_pat_seed, freq_seed, freq_pat):
        A = freq_pat_seed
        B = freq_seed * freq_pat
        pmi = None
        if A != 0 and B != 0:
            pmi = 18 + math.log10( 1.0 * A / B )
        return pmi      
        
    def generate_patterns(self):
        
        seeds = self.my_config.get_seeds()
        for seed in seeds:
            self.get_patterns_for_seed(seed)
            

       
       
    def save_and_clean(self):
        filename_patterns = self.my_config.get_filename_results_pattern()
        
        percent = self.my_config.get_percent_selected_patterns()        
        max_patterns = percent * len(self.list_pattern_pmi) / 100
        min_num_seeds_to_appear_with = self.my_config.get_min_num_seeds_to_appear_with()
        
        #ROOT
        root = etree.Element('patterns')
        num_selected = 0 
        for num_pattern, (pattern, overall_pmi) in enumerate(self.list_pattern_pmi):
            seeds_pmi =  self.results_for_pattern[pattern]
            active = '0'
            if num_selected < max_patterns: # Could be selected
                if len(seeds_pmi) >= min_num_seeds_to_appear_with: # will be selected
                    active = '1'
                    num_selected += 1
                
                       
            ele = etree.Element('pattern',attrib={'pmi':str(overall_pmi),'active':active,'num':str(num_pattern)})
            val = etree.Element('value')
            val.text = pattern
            ele.append(val)
            root.append(ele)
            for seed, pmi in self.results_for_pattern[pattern]:
                ele_seed = etree.Element('seed',attrib={'word':seed,'pmi':str(pmi)})
                ele.append(ele_seed)
        
        tree = etree.ElementTree(element=root)
        tree.write(filename_patterns,encoding='UTF-8',pretty_print=True,xml_declaration=True)
        print>>sys.stderr,'Patterns saved in',filename_patterns
        print>>sys.stderr,'   Total patterns: ',len(self.list_pattern_pmi)
        print>>sys.stderr,'   Number of active patterns:',num_selected
        del self.results_for_pattern
        del self.list_pattern_pmi
        
         
        filename_freq = self.my_config.get_filename_overall_frequency()
        fic2 = open(filename_freq,'wb')
        cPickle.dump(self.overall_frequency,fic2)
        print>>sys.stderr,'Saved overall freq for pattern, total patterns:',len(self.overall_frequency)
        fic2.close()
        del self.overall_frequency
        self.overall_frequency = {}
        
      
    
    
    def load_data(self):
        self.active_patterns = []
        filename_patterns = self.my_config.get_filename_results_pattern()
        
        tree = etree.parse(filename_patterns,etree.XMLParser(remove_blank_text=True))
        
        for patter_ele in tree.findall('pattern'):
            active = patter_ele.get('active')
            if active == '1':
                pattern = patter_ele.find('value').text
                pmi = float(patter_ele.get('pmi'))
                self.active_patterns.append((pattern,pmi))
                
        print>>sys.stderr,'Loaded',len(self.active_patterns),'active patterns'
        
        filename_freq = self.my_config.get_filename_overall_frequency()
        fic2 = open(filename_freq,'rb')
        self.overall_frequency = cPickle.load(fic2)
        print>>sys.stderr,'Loaded overall freq for pattern, total patterns:',len(self.overall_frequency)
        fic2.close()
        
            
    def print_patterns(self):
        for p, res in self.results_for_pattern.items():
            print 'Pattern:',p
            for seed, pmi in res:
                print '  ',seed,' ',pmi
            print
        
        
    def agglomerate_patterns_by_avg(self):
        self.list_pattern_pmi = []
        for pattern, pairs in self.results_for_pattern.items():
            avg_pmi = sum(pmi_with_seed for seed,pmi_with_seed in pairs)/len(pairs)
            self.list_pattern_pmi.append((pattern,avg_pmi))
        self.list_pattern_pmi.sort(key=itemgetter(1),reverse=True)

        
    def get_candidates_words(self):
        self.pmi_for_target = {}

        print>>sys.stderr,'Generating candidate words'
        for n, (pattern, pmi) in enumerate(self.active_patterns):
            # Pattern can be * journalisten en
            # We need to query and get those words
            print>>sys.stderr,'  Processing pattern',pattern,'pmi',pmi,'('+str(n)+' of '+str(len(self.active_patterns))+')'
            print>>sys.stderr,'    Querying for all the words matching the pattern'
            target_words_results = self.query(pattern,fixed='hidden')
            print>>sys.stderr,'    Number of words:',len(target_words_results)
            freq_pattern = self.get_overall_frequency(pattern)
            for target_word_item in target_words_results:
                target_word = target_word_item.get_word()
                
                freq_pattern_target = target_word_item.get_hits()
                freq_target = self.get_overall_frequency(target_word)
                
                this_pmi = self.pmi(freq_pattern_target, freq_target, freq_pattern)
                print>>sys.stderr,'    Target word:',target_word
                print>>sys.stderr,'        Freq target:',freq_target
                print>>sys.stderr,'        Freq target+pattern:',freq_pattern_target
                print>>sys.stderr,'        Freq pattern:',freq_pattern
                print>>sys.stderr,'        PMI:',this_pmi
                                
                if this_pmi is not None:
                    if target_word in self.pmi_for_target:
                        self.pmi_for_target[target_word].append(this_pmi)
                    else:
                        self.pmi_for_target[target_word] = [this_pmi]
                    
 
        
    def agglomerate_candidate_words_avg(self):
        self.final_target_words = []
        for target_word, list_pmis in self.pmi_for_target.items():
            avg_pmi  = sum(pmi for pmi in list_pmis) / len(list_pmis)
            self.final_target_words.append((target_word,avg_pmi))
            
    def generate_candidate_words(self):
        # This will create self.pmi_for_target, which contains for each target word a list of pmi associated
        # ['target'] == [pm1, pm2. pm3]
        self.get_candidates_words()
        
        #This will created a list self.final_target_words ==> (A,pmi), (B,pmi)...
        self.agglomerate_candidate_words_avg()
        
        self.final_target_words.sort(key=itemgetter(1),reverse=True)
        
        self.save_to_csv()
        
    def print_to_screen(self):
        print '%20s %15s' % ('Target word','Average PMI')
        print '#' *50                             
        for tw,pmi in self.final_target_words:
            print '%20s %10.5f' % (tw,pmi)
        print '#' *50                             

    def save_to_csv(self):
        filename = self.my_config.get_filename_csv()
        fic = open(filename,'w')
        for tw,pmi in self.final_target_words:
            fic.write('%s;%f\n' % (tw,pmi))
        fic.close()
        print>>sys.stderr,'Target words saved in ',filename
    
if __name__ == '__main__':
    print '''
       This script can not be called directly, use these scripts instead:
       1) create_patterns.py config.cfg  --> To generate a list of patterns from a seed list
       2) generate_candidate_words.py config.cfg --> To extract a set of candidate words from the previous set of patterns
       
       The format of the config file is:
            [general]
            output_folder = my_folder                       The output folder where you want to store all the generated data
            seeds = toeristisch;interessante                List of ; separated seeds
            ngram_len = 3                                   Length of ngrams to generate, with 5 it will use 5-grams, 4-grams, 3-grams and 2-grams
            percent_selected_patterns = 25                  Percentage of first patterns sorted according to PMI to be selected
            accept_patterns_with_at_least_num_seeds = 2     Minimum number of seed that a pattern must be found with to be considered as active

            [google_web_query]
            limit_per_query = 100                           Limit in the query for ngrams
            min_freq_for_hit = 40                           Minimum frequency allowed for an n-gram
    
        Example of usage:
        1) Modify or create a configuration file with your setting (my_config.cfg)
        2) Run the create pattern extractor:
            python create_patterns.py my_config.cfg > log.out 2> log.err &      (log info will be in the log.err file)
        3) Modify the file $folder/extracted_patterns.xml
        3) Run the generate_candidate_words (you need to use the same configuration file as in step 1)
            python generate_candidate_words.py my_config.cfg > log.out 2> log.err & (info in log.err)
            
    '''