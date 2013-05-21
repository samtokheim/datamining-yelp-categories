from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol
from itertools import permutations
import json
import math
import re

class BusinessSim(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol
    
    # go through each review - if the business category is in businesses dict, yield the business_id and the word.
    def get_words(self, _, record):    
        if record['type'] == 'review':
            #Turn the string or review words into a list
            words = list(record['text'])            
            #Iterate through each word in the review
            for word in words:                   
                yield record['business_id'], word            
        
    # create word set for each business_id
    def get_word_set(self, business_id, words):    
        words_list = set(words)
        
        yield business_id, list(words_list)  
    
    # combine both inputs into output value     
    def combine_review_words(self, business_id, review_words):
    
        yield 'foo', [business_id, review_words]             
            
    # compare word lists for each business, calculate jaccard coefficient       
    def compare_businesses(self, _, business_reviews):
        for biz1, biz2 in permutations(business_reviews, 2):            
            all_words = (set(biz1[1] + biz2[1]))
            jaccard_denom = len(all_words)
            common_words = (set(biz1[1]) & set(biz2[1]))            
            jaccard_numer = len(common_words)            
            jaccard_coefficient = float(jaccard_numer) / jaccard_denom

            yield [biz1[0], biz1[1]], [biz2[0], jaccard_coefficient]

    # make a comprehensive list of businesses with business_id, word sets, and jaccard relationships with each other business_id
    def make_business_list(self, biz1, biz2s):        
        biz2s = list(biz2s)
        biz1 = list(biz1)
        
        yield biz1, biz2s
    
    def steps(self):

        return [self.mr(mapper=self.get_words, reducer=self.get_word_set), 
                self.mr(mapper=self.combine_review_words, reducer=self.compare_businesses),
                self.mr(reducer=self.make_business_list)]

if __name__ == '__main__':
    BusinessSim.run()
