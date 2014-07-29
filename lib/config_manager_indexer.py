import ConfigParser
import os

class Config_manager:
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.out_folder = None

    def set_current_folder(self,t):
        self.cwd = t

    def set_config(self,file_cfg):
        self.config.read(file_cfg)
        output_folder_cfg = self.config.get('general','output_folder')
        out_folder = ''
        if os.path.isabs(output_folder_cfg):
            self.out_folder = output_folder_cfg
        else:
            self.out_folder = os.path.join(self.cwd,output_folder_cfg)
        
    def get_output_folder(self):
        return self.out_folder
    
    def get_remove_output_folder_if_exists(self):
        r = False
        if self.config.has_option('general', 'remove_output_folder_if_exists'):
            r = self.config.getboolean('general', 'remove_output_folder_if_exists')
        return r
    
    def get_file_with_list_inputs(self):
        if self.config.has_option('general', 'file_with_list_inputs'):
            return self.config.get('general', 'file_with_list_inputs')
        else:
            return None
        
    def get_include_sentence_delimiters(self):
        r = True
        if self.config.has_option('general','include_sentence_delimiters'):
            r = self.config.getboolean('general','include_sentence_delimiters')
        return r
    
    def get_filename_for_ngrams(self,n):
        my_name = 'ngrams.len_%s.txt' % n
        return os.path.join(self.get_output_folder(),my_name)
    
    def get_filename_for_idx(self,n):
        my_name = 'ngrams.len_%s.idx.txt' % n
        return os.path.join(self.get_output_folder(),my_name)
    
    def get_cwd(self):
        return self.cwd
    
    def get_max_ngram_len(self):
        if self.config.has_option('general','max_ngram_len'):
            return int(self.config.get('general','max_ngram_len'))
        else:
            return 3

    def get_min_ngram_len(self):
        if self.config.has_option('general','min_ngram_len'):
            return int(self.config.get('general','min_ngram_len'))
        else:
            return 1
    def get_punctuation(self):
        my_list = []
        if self.config.has_option('general', 'punctuation'):
            p =  self.config.get('general', 'punctuation')
            my_list = p.strip().split(' ')
        print my_list
        return my_list
    
    def get_convert_to_lowercase(self):
        c = False   #Default
        if self.config.has_option('general','convert_to_lowercase'):
            c = self.config.getboolean('general','convert_to_lowercase')
        return c
    
    def get_subset_index_for(self):
        s = None
        if self.config.has_option('general','subset_index_for'):
            s = self.config.get('general','subset_index_for')
        return s
    
       
