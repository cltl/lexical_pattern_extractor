import sys
import os
import shutil
import math
import re

from collections import defaultdict
from operator import itemgetter
from subprocess import Popen,PIPE
from KafNafParserPy import KafNafParser

METADATA = 'metadata.txt'
DELIMITER = '##'

class Cngram_index_creator:
    def __init__(self):
        self.list_input_files = []
        self.punctuation = []
        self.convert_to_lowercase = False
        self.datafile_for_ngram = {}
        self.datafile_for_ngram_subset = {}
        self.max_ngram_len = 1
        self.min_ngram_len = 1
        self.input_file_list = None
        self.out_folder = None
        self.remove_out_if_exists = True
        self.include_sentence_delimiters = True
        self.min_freq_for_ngram = 1
        
    def set_min_freq_for_ngram(self,m):
        self.min_freq_for_ngram = m
        
    def set_include_sentence_delimiters(self,flag):
        self.include_sentence_delimiters = flag
        
    def set_remove_out_if_exists(self,flag):
        self.remove_out_if_exists = flag
        
    def set_out_folder(self,of):
        self.out_folder = of

    def set_punctuation(self,string_punc):
        self.punctuation = [c for c in string_punc]
        
    def set_convert_to_lowercase(self,flag):
        self.convert_to_lowercase = flag
        
    def set_max_ngram_len(self,m):
        self.max_ngram_len = m
        
    def set_min_ngram_len(self,m):
        self.min_ngram_len = m
        
    def set_input_file_list(self,f):
        self.input_file_list = f
        
      
       
    ## LOADING INPUT FILES 
    def load_input_files_from_file(self,filename):
        fic = open(filename,'r')
        for line in fic:
            file = line.strip()
            self.list_input_files.append(file)
                     
    def load_input_files(self):
        if self.input_file_list is not None:
            self.load_input_files_from_file(self.input_file_list)
    ## END LOADER FILES
            
    def get_file_desc_for_ngram(self,n,subset=False):
        if not subset:
            datafile = self.datafile_for_ngram
            suffix = ''
        else:
            datafile = self.datafile_for_ngram_subset
            suffix = '.subset'
            
        n= str(n)
        if n in datafile:
            filengram, fileidx, filedesc = datafile[str(n)]
        else:
            my_ngram_name = 'ngrams.len_%s.txt' % n
            filengram = os.path.join(self.out_folder,my_ngram_name)
            
            my_idx_name = 'ngrams.len_%s.idx.txt' % n 
            fileidx = os.path.join(self.out_folder,my_idx_name)
             
            filedesc = open(filengram,'w')
            datafile[n] = (filengram,fileidx,filedesc)
        return filedesc
    
    
              
    ## PROCESSING
    def process_single_file(self,file):
        try:
            xml_obj = KafNafParser(file)
        except:
            print>>sys.stderr,'Error parsing',file,': skipped'
            return        


        print>>sys.stderr,'Processing file', os.path.basename(file), 'Type:',xml_obj.get_type()
        sentences = []
        current_sent = []
        this_sent = None
                 
                 
               
         
        pos_for_wid = {} ## For each token id (wid) the pos of it
        for term in xml_obj.get_terms():
            w_ids = term.get_span().get_span_ids()
            pos = term.get_pos()
            for wid in term.get_span().get_span_ids():
                pos_for_wid[wid] = pos

            
        for token in xml_obj.get_tokens():
            wid = token.get_id()
            value = token.get_text()
            if self.convert_to_lowercase:
                value = value.lower()
                
            if value in self.punctuation:
                value = 'PUN'
                
            if value == '*':
                value = 'STAR'
            
            sentence = token.get_sent()
            if this_sent is not None and sentence != this_sent:  ## There is a new sent
                sentences.append(current_sent)
                current_sent = []
            current_sent.append((wid,value))
            this_sent = sentence
        ## Add the last sentence as well
        sentences.append(current_sent)
        
        for sentence in sentences:
            if self.include_sentence_delimiters:
                sentence.insert(0,('xxx','<S>'))
                sentence.append(('xxx','</S>'))
        
            for idx in range(0,len(sentence)):
                for ngramlen in range(self.min_ngram_len,self.max_ngram_len+1):
                    file_desc = self.get_file_desc_for_ngram(ngramlen)
                    start = idx
                    end = start + ngramlen
                    if end <= len(sentence):
                        this_ngram = '\t'.join(value for wid, value in sentence[start:end])
                        this_ngram_pos = '\t'.join(pos_for_wid.get(wid,'X') for wid, value in sentence[start:end])
                        file_desc.write(this_ngram.encode('utf-8')+'\t'+DELIMITER+'\t'+this_ngram_pos+'\n')

                                 
                        
    def close_all(self):
        for ngramlen, datafile in self.datafile_for_ngram.items():
            filengram, _ , filedesc = datafile
            print>>sys.stderr,'Closing file ',filengram,
            filedesc.close()
            print>>sys.stderr,' ... OK'
            
        for ngramlen, datafile in self.datafile_for_ngram_subset.items():
            filengram, _ , filedesc = datafile
            print>>sys.stderr,'Closing file subset ',filengram,
            filedesc.close()
            print>>sys.stderr,' ... OK'
            
            
    def create_indexes(self,subset=False):
        if not subset:
            datafile = self.datafile_for_ngram
            suffix = ''
        else:
            datafile = self.datafile_for_ngram_subset
            suffix = '.subset'
        
        metadata = open(os.path.join(self.out_folder,METADATA+suffix),'w')
        
        for ngramlen, datafile in datafile.items():
            filengram, fileidx, _ = datafile
            metadata.write('%s %s %s\n' %(ngramlen,os.path.basename(filengram),os.path.basename(fileidx)))
            
            print>>sys.stderr,'Creating index'
            print>>sys.stderr,'  Input ngram file:',filengram
            freq_dic = defaultdict(int)
            
            ## Read the file with ngrams
            fic_in = open(filengram,'r')
            for ngram in fic_in:
                freq_dic[ngram.decode('utf-8').rstrip()] += 1
            fic_in.close()
                   
            ## Write the index to the output

            fic_out = open(fileidx,'w')
            sorted_list = sorted(freq_dic.items(),key=itemgetter(1),reverse=True)
            del freq_dic
            for ngram,freq in sorted_list:
                if freq >= self.min_freq_for_ngram:
                    fic_out.write('%d %s\n' %(freq,ngram.encode('utf-8')))
            fic_out.close()
            del sorted_list
            print>>sys.stderr,'  Output index ngram file:',fileidx
        metadata.close()
                
    def create_ngram_index(self):
    
        self.load_input_files()
        
        ##Create outfolder
        if os.path.exists(self.out_folder):
            if self.remove_out_if_exists:
                shutil.rmtree(self.out_folder)
                os.mkdir(self.out_folder)
            else:
                pass #Nothing if it exists and we dont want to remove it
        else:
             os.mkdir(self.out_folder)
        ####
             
        #Create the raw lists of ngrams
        for file in self.list_input_files:
            self.process_single_file(file)    
        self.close_all()
        
        # Create the indexes
        self.create_indexes()
        
        if len(self.datafile_for_ngram_subset) != 0: ## if there are data files created
            self.create_indexes(subset=True)
        
class Citem:
    def __init__(self,line,with_pos=False):
        self.hits = None
        self.word = None
        self.tokens = None
        self.pos = []
        if not with_pos:
            self.load_from_string(line)
        else:
            self.load_from_string_with_pos(line)
            
    def load_from_string_with_pos(self,line):
        # Example line: 22865,"de server van    DEL    pos1 pos2 pos3"
        line = line.decode('utf-8').strip()
        pos = line.find(' ')
        self.hits = int(line[:pos])
        all_tokens = line[pos+1:].split()
        position_of_delimiter = len(all_tokens)/2
        
        #WORDS
        self.tokens = all_tokens[:position_of_delimiter]
        self.word = ' '.join(self.tokens)
        
        #POS
        self.pos = all_tokens[position_of_delimiter+1:]
 
    def load_from_string(self,line):
        ## Example line: 22865,"de server van"
        line = line.decode('utf-8').strip()
        
        pos = line.find(' ')
        self.hits = int(line[:pos])
        self.tokens = line[pos+1:].split()
        self.word = ' '.join(self.tokens)
        
    def remove_this(self,str_to_remove):
        tokens_to_remove = str_to_remove.split()
        # self.tokens = [u'quite', u'spacious', u'and']
        # self.word = 'quite spacious and'
        # str_to_remove = 'quite * and'
        # tokens_to_remove = [quite,*,and]
        only_this = []
        only_this_pos = []
        if len(tokens_to_remove) == len(self.tokens):
            for i in range(len(tokens_to_remove)):
                if tokens_to_remove[i] != self.tokens[i]:
                    only_this.append(self.tokens[i])
                    if len(self.pos) != 0:
                        only_this_pos.append(self.pos[i])

            if len(only_this) != 0:
                self.tokens = only_this
                self.word = ' '.join(self.tokens)
                self.pos = only_this_pos
        
            
    def __str__(self):
        if self.word is not None and self.hits is not None:
            s = str(self.tokens)+' POS:'+str(self.pos)+' -> '+str(self.hits)+' hits'
        else:
            s = 'None'
        return s
    
    def __repr__(self):
        return self.__str__()
    
    def get_hits(self):
        return self.hits
    
    def get_word(self):
        return self.word
    
    def get_tokens(self):
        return self.tokens
    
    def get_pos(self):
        return self.pos
    
class Cngram_index_enquirer:
    def __init__(self,folder):
        self.folder = folder
        self.datafiles_for_ngram_len = {}
        
        self.load_datafiles()
        
    def load_datafiles(self):
        metadata = os.path.join(self.folder,METADATA)
        if not os.path.exists(metadata):
            print>>sys.stderr,'Metadata file',metadata,' not found'
            print>>sys.stderr,'Are you sure the folder is a correct ngram index folder ?'
            sys.exit(-1)
        fic = open(metadata,'r')
        for line in fic:
            ngramlen, filengram, fileidx = line.rstrip().split(' ')
            filengram = os.path.join(self.folder,filengram)
            fileidx = os.path.join(self.folder,fileidx)
            
            self.datafiles_for_ngram_len[ngramlen] = (filengram,fileidx)
            #print>>sys.stderr,'Ngram len:',ngramlen,' file:',fileidx
        fic.close()
        
    def convert_querystr(self,querystr):
        ## The patterns are stored like:
        ## freqWHITESPACEw1TABw2TABw3TABw4$
        ## querystr can be something like "the * of"
        
        if isinstance(querystr, list):
            tokens = querystr
            ngramlen = len(tokens)
        else:
            #1 split by whitespaces:
            tokens = querystr.split()
            ngramlen = len(tokens)
        
        # replace * by .+
        for idx in range(0,len(tokens)):
            if tokens[idx] == '*': tokens[idx] = '.+'
            else: tokens[idx] = re.escape(tokens[idx])
        
        custom_query = ' '+'\\t'.join(tokens)+'\\t'+DELIMITER
                         
        return ngramlen, custom_query
        
        
    def run_grep(self,custom_query,fileidx,only_match,query_str=None):
        items = []
        os.environ['LC_ALL'] = 'C'
        cmd = 'grep --mmap -P "'+custom_query+'" '+fileidx
        grep  = Popen(cmd, stdout=PIPE, stderr=PIPE , shell = True)
        out_stream, err_stream = grep.communicate()
        #As could be several identical patterns like was-goed V-D or was-goed V-N we must filter out this
        already_returned = set()
        for line in out_stream.splitlines():
            new_item = Citem(line,with_pos=True)
            if only_match:
                new_item.remove_this(query_str)
            if new_item.word not in already_returned:
                items.append(new_item)
                already_returned.add(new_item.word)
            else:
                pass
                #print>>sys.stderr,'Skipped ',str(new_item),'as was already returned' 
                
        return items
            
        
    def query(self,querystr, only_match=False):
        ngramlen, custom_query = self.convert_querystr(querystr)
        if str(ngramlen) in self.datafiles_for_ngram_len:
            fileidx = self.datafiles_for_ngram_len[str(ngramlen)][1]    #filngram, fileidx
            items = self.run_grep(custom_query, fileidx,only_match,querystr)
            return items
        else:
            print>>sys.stderr,'Query ',querystr,'is a '+str(ngramlen)+'-gram and there is no index for that size'
            return None
                            
class Cconstrastive_analyser:
    def __init__(self,folder):
        self.folder = folder
        self.datafiles_for_ngramlen = {}
        self.datafiles_for_ngramlen_subset = {}
        
        self.load_datafiles()

        self.min_overall_freq = 5
        
    def load_datafiles(self):
        for metadatafilena, datafile in [(METADATA,self.datafiles_for_ngramlen), (METADATA+'.subset',self.datafiles_for_ngramlen_subset)]:
        
            metadata = os.path.join(self.folder,metadatafilena)
            if not os.path.exists(metadata):
                print>>sys.stderr,'Metadata file',metadatafilena,' not found'
                print>>sys.stderr,'Are you sure the folder is a correct ngram index folder ?'
                sys.exit(-1)
            
            fic = open(metadata,'r')
            for line in fic:
                ngramlen, filengram, fileidx = line.rstrip().split(' ')
                filengram = os.path.join(self.folder,filengram)
                fileidx = os.path.join(self.folder,fileidx)
                datafile[ngramlen] = (filengram,fileidx)
            #print>>sys.stderr,'Ngram len:',ngramlen,' file:',fileidx
            print>>sys.stderr,'Loaded from',metadatafilena,' -->', len(datafile),'files'
        fic.close()
        
    def load_ngrams_from_idx(self,file_idx):
        ngram_freq = {}
        freq_total = 0
        fic = open(file_idx)
        for line in fic:
            #freq PATTERN
            fields = line.strip().split(' ')
            freq = int(fields[0])
            ngram_freq[fields[1]] = freq
            freq_total += freq
        fic.close()
        return ngram_freq, freq_total
    
    def basic_likelihood(self,ngram_all,ngram_subset):
        ngram_list = []
        for subset_ngram, freq_subset in ngram_subset.items():
            freq_overall = ngram_all.get(subset_ngram,0)
            if freq_overall >= self.min_overall_freq:
                ngram_list.append((subset_ngram,freq_subset*1.0/freq_overall,freq_subset,freq_overall))
        ngram_list.sort(key=itemgetter(1),reverse=True)
        for n, (ngram, value,fr,fo) in enumerate(ngram_list[:100]):
            print>>sys.stderr,"%d) %s LIKELIHOOD=%f.2 freq_rel=%d freq_total=%d" % (n,ngram,value,fr,fo)
        print>>sys.stderr
        
    def mutual_information(self,ngram_all, N, ngram_subset, N_subset):
        ngram_list = []
        for subset_ngram, freq_subset in ngram_subset.items():
            freq_overall = ngram_all.get(subset_ngram,0)
            if freq_overall >= self.min_overall_freq:
                prob_word_in_subset = float(freq_subset) / N_subset
                prob_word_in_all = float(freq_overall) / N
                mut_inf = math.log10(prob_word_in_subset/prob_word_in_all)
                ngram_list.append((subset_ngram,mut_inf,freq_subset,freq_overall))
        ngram_list.sort(key=itemgetter(1),reverse=True)
        for n, (ngram, value,fr,fo) in enumerate(ngram_list[:100]):
            print>>sys.stderr,"%d) %s MUTUAL_INFO=%f.2 freq_rel=%d freq_total=%d" % (n,ngram,value,fr,fo)
        print>>sys.stderr
        
            
        
    def process_files(self,file_idx_all, file_idx_subset):
        print>>sys.stderr,'Processing ', os.path.basename(file_idx_all),'<-->',os.path.basename(file_idx_subset)
        if not os.path.exists(file_idx_all):
            print>>'Skipping because',file_idx_all,' can not be found'
            return None
        if not os.path.exists(file_idx_subset):
            print>>'Skipping because',file_idx_subset,' can not be found'
            return None
        
        
        ngram_freq_all, total_words = self.load_ngrams_from_idx(file_idx_all)
        print>>sys.stderr,'\tNum ngrams loaded (all set)',os.path.basename(file_idx_all),':',len(ngram_freq_all)
        
        ngram_freq_subset, total_words_subset = self.load_ngrams_from_idx(file_idx_subset)
        print>>sys.stderr,'\tNum ngrams loaded (subset)',os.path.basename(file_idx_subset),':',len(ngram_freq_subset)

        #self.basic_likelihood(ngram_freq_all, ngram_freq_subset)
        self.mutual_information(ngram_freq_all, total_words, ngram_freq_subset, total_words_subset)
        
        return None    
        
        
        
    def run(self):
        for ngram_len, (file_raw, file_idx) in self.datafiles_for_ngramlen.items():
            if ngram_len in self.datafiles_for_ngramlen_subset:
                if ngram_len == '1':
                    file_raw_subset, file_idx_subset = self.datafiles_for_ngramlen_subset[ngram_len]
                    self.process_files(file_idx,file_idx_subset)
                
        
      