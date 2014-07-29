#!/usr/bin/env python



import sys
import operator
import math
import string

print 'Moved to opener stuff!!!! 2nd april 2014'

from lib.ngram_frequency_index import Cngram_index_enquirer

stop_words = {}
stop_words['nl'] = set(['andere', 'deze', 'over', 'zal', 'ge', 'niet', 'als', 'daar', 'moet', 'had', 'te', 'toch', 'bij', 'niets', 'dan', 
                        'nog', 'maar', 'dat', 'wordt', 'doch', 'geen', 'hij', 'worden', 'die', 'een', 'dit', 'iets', 'en', 'altijd', 
                        'haar', 'ze', 'mijn', 'kunnen', 'zonder', 'naar', 'er', 'doen', 'omdat', 'iemand', 'wezen', 'men', 'met', 
                        'je', 'ja', 'toen', 'om', 'tegen', 'of', 'kon', 'voor', 'onder', 'hier', 'geweest', 'veel', 'op', 'wie', 'zelf', 
                        'wil', 'zo', 'zijn', 'ons', 'het', 'heeft', 'van', 'eens', 'uw', 'tot', 'heb', 'hem', 'dus', 'was', 'door', 
                        'hun', 'zich', 'me', 'wat', 'ben', 'zij', 'der', 'aan', 'werd', 'meer', 'alles', 'reeds', 'is', 'al', 'ik', 
                        'uit', 'want', 'in', 'mij', 'na', 'zou', 'waren', 'nu', 'de', 'kan', 'hoe', 'ook', 'hebben', 'u'])

stop_words['en'] = set(['all', 'just', 'being', 'over', 'both', 'through', 'yourselves', 'its', 'before', 'herself', 'had', 'should', 
                        'to', 'only', 'under', 'ours', 'has', 'do', 'them', 'his', 'very', 'they', 'not', 'during', 'now', 'him', 'nor', 
                        'did', 'this', 'she', 'each', 'further', 'where', 'few', 'because', 'doing', 'some', 'are', 'our', 'ourselves', 
                        'out', 'what', 'for', 'while', 'does', 'above', 'between', 't', 'be', 'we', 'who', 'were', 'here', 'hers', 'by', 
                        'on', 'about', 'of', 'against', 's', 'or', 'own', 'into', 'yourself', 'down', 'your', 'from', 'her', 'their', 
                        'there', 'been', 'whom', 'too', 'themselves', 'was', 'until', 'more', 'himself', 'that', 'but', 'don', 'with', 
                        'than', 'those', 'he', 'me', 'myself', 'these', 'up', 'will', 'below', 'can', 'theirs', 'my', 'and', 'then', 
                        'is', 'am', 'it', 'an', 'as', 'itself', 'at', 'have', 'in', 'any', 'if', 'again', 'no', 'when', 'same', 'how', 
                        'other', 'which', 'you', 'after', 'most', 'such', 'why', 'a', 'off', 'i', 'yours', 'so', 'the', 'having', 'once'])

def query(folder, query, mutual_info=False):
    found = []
    enquirer = Cngram_index_enquirer(folder)
    items = enquirer.query(query,only_match = True)
    frequency_pattern = 0 ## This will store the total frequency of the pattern, for instance: een goed *
    if mutual_info:
        for item in items:
            frequency_pattern += item.get_hits()
            
    #print>>sys.stderr, 'Query: ', query
    for n, item in enumerate(items):
        token_str = item.get_word()
        list_pos = ''.join(item.get_pos())  ##We create a string out of a list, like GDA
        #print>>sys.stderr,'  Token',token_str
        hits = item.get_hits()
        if mutual_info:
            items_for_token = enquirer.query(token_str,False)
            freq_token = items_for_token[0].get_hits()
            #value = math.log10(hits*1.0 / (frequency_pattern * freq_token))
            value = math.log10(hits*1.0 / (frequency_pattern))
            #print>>sys.stderr,'   Freq pattern', frequency_pattern
            #print>>sys.stderr,'   Freq token', freq_token
            #print>>sys.stderr,'   Freq pat+tok', hits
            #print>>sys.stderr,'   Value', value 
            found.append((token_str,value))
        else:
            #print>>sys.stderr,'   Value',hits
            found.append((token_str,list_pos, hits))
    return found
        
def filter_targets(map_targets, lang):
    allow_only_these_pos = ['N']
    filtered_targets = []
    for (target, pos), list_values in map_targets.items():
        allow_this_target = False
        for allowed_pos in allow_only_these_pos:
            if allowed_pos in pos:
                allow_this_target = True
                break
            
        if allow_this_target:
            #avg_val = sum(list_values) / len(list_values)
            val = sum(list_values)
            if target not in stop_words[lang]:
                if target not in string.punctuation:
                    if val > 1:
                        filtered_targets.append((target,pos,list_values))
    return sorted(filtered_targets,key=lambda this_tuple: sum(this_tuple[2]), reverse=True)

def filter_expressions(map_expressions, lang):
    filtered_exps = []
    allow_only_these_pos = ['G']    #Adjectives
    for (exp,pos), list_values in map_expressions.items():
        allow_this_exp = False
        for allowed_pos in allow_only_these_pos:
            if allowed_pos in pos:
                allow_this_exp = True
                break
        
        if allow_this_exp:
            val = sum(list_values)
            #avg_val = sum(list_values) / len(list_values)
            if exp not in stop_words[lang]:
                if exp not in string.punctuation:
                    if val > 1:
                        filtered_exps.append((exp,pos,list_values))
    return sorted(filtered_exps,key=lambda this_tuple: sum(this_tuple[2]), reverse=True)
                                                                          

if __name__ == '__main__':
    lang = 'en'
    if lang == 'nl':
        folder = 'indexes/raw_hotel_reviews_nl_pos' ##indexes/raw_hotel_reviews_en
        starting_seeds = ['goed','goede','slecht','slechte','leuk','leuke','afschuwelijk','afschuwelijke','vriendelijk','onvriendelijke','lekker','lekkere','vies','vieze']
        patterns = []
        patterns.append('een [EXP] [TARGET]')
        patterns.append('het [EXP] [TARGET]')
        patterns.append('de [EXP] [TARGET]')   
    elif lang == 'en': 
        folder = 'indexes/raw_hotel_reviews_en_pos_max4'
        starting_seeds = ['good','bad','nice','friendly']
        patterns = []
        patterns.append('a [EXP] [TARGET]')
        patterns.append('the [EXP] [TARGET]')
        patterns.append('such [EXP] [TARGET]')   

    all_expressions = {}
    for seed in starting_seeds:
        all_expressions[seed] = [1000]
    all_targets = {}
    
    new_expressions = starting_seeds
    
    num_iter = 0
    MAX_ITER = 5
    while True:
        print 'Iteration num:',num_iter
        if num_iter > MAX_ITER:
            break
        
        ##############################################################
        ## TARGET PART #
        ##############################################################
        targets = {}  ## targets['hotel'] = [1.0, 3.2, 0.34]
        print '  Finding targets'
        for ns, seed in enumerate(new_expressions):
            print '    Seed ',ns,'of',len(new_expressions),':', seed.encode('utf-8')
            for pattern in patterns:
                pattern = pattern.replace('[EXP]',seed)
                pattern = pattern.replace('[TARGET]','*')
                print '      Pattern:',pattern.encode('utf-8')
                
                possible_targets = query(folder,pattern,mutual_info=False)
            
                for target, postags, value in possible_targets:
                    if value > 50:   #No include targets with frequency 1
                        #print>>sys.stderr,target.encode('utf-8'),value
                        if (target, postags) not in targets:
                            targets[(target,postags)] = []
                        targets[(target,postags)].append(value)

        
        filtered_targets = filter_targets(targets, lang)  # List of (token, val)
        del targets
        ##############################################################
        

        
        new_targets = []
        for target, pos, list_values in filtered_targets:
            if target in all_targets:
                all_targets[target].extend(list_values)
            else:
                if target not in all_expressions:
                    all_targets[target] = list_values
                    new_targets.append(target)
                
    
        ##############################################################
        ## EXPRESSION PART #
        ##############################################################   
        print '  Expression'
        expressions = {}
        for nt, target in enumerate(new_targets):
            print '  Target',nt,'of',len(new_targets),':',target.encode('utf-8')
            for pattern in patterns:
                pattern = pattern.replace('[EXP]','*')
                pattern = pattern.replace('[TARGET]',target)
                print '    Pattern:', pattern.encode('utf-8')        
                possible_exps = query(folder,pattern, mutual_info=False)
                
                for exp, postag, value_exp in possible_exps:
                    if value_exp >= 50:
                        if (exp,postag) not in expressions:
                            expressions[(exp,postag)] = []
                        expressions[(exp,postag)].append(value_exp)
        filtered_expressions = filter_expressions(expressions, lang)
        
        new_expressions = []
        for exp, postag, value in filtered_expressions:
            if exp in all_expressions:
                all_expressions[exp].extend(list_values)
            else:
                if exp not in all_targets:
                    all_expressions[exp] = list_values
                    new_expressions.append(exp)
        
        
        
        print 'Iteration number:', num_iter
        num_iter += 1
        
        print '    New targets on this iteration'
        for n, target in enumerate(new_targets):
            print '      tar_'+str(n),target.encode('utf-8')
        print
        print '    New expressions on this iteration'
        for n, exp in enumerate(new_expressions):
            print '      exp_'+str(n),exp.encode('utf-8')
        print   
        
    
    #######
    print '#'*50
    print 'FINAL LEXICONS'
    print '  EXPRESSIONS'
    for n, (exp, values) in enumerate(sorted(all_expressions.items(),key=lambda pair: sum(pair[1]), reverse=True)):
        print '\t','exp_'+str(n), exp.encode('utf-8') 
        print '\t   Total values:',len(values)
        print '\t   Sum values (sorted by this):',sum(values)
        print '\t   Avg total freq',sum(values)*1.0/len(values)
    print '  TARGETS'
    for n, (tar, values) in enumerate(sorted(all_targets.items(),key=lambda pair: sum(pair[1]), reverse=True)):
        print '\t','tar'+str(n), tar.encode('utf-8')
        print '\t   Total values:',len(values)
        print '\t   Sum values (sorted by this):',sum(values)
        print '\t   Avg total freq',sum(values)*1.0/len(values)
    print '#'*50   
        

    sys.exit(0)
        
  