import json
import re

"""
##############
READ IN DATA

Data sets used (and grep commands used to create them)

1. yelp_academic_dataset.json - full listings of all yelp reviews and businesses
2. yelp_businesses.json - extracted all business listings from yelp_academic_dataset:
    grep 'type": "business' yelp_academic_dataset.json > yelp_businesses.json
3. review_set25000.json - manageable sized set of reviews:
    grep -m 25000 'type": "review' yelp_academic_dataset.json > review_set25000.json    
4. review_set.json - huge file of all the reviews. use if you have a powerful processor!    
5. 5k_common_words.csv - list of 5000 most common words in English language - found at http://www.wordfrequency.info/top5000.asp
    
##############
"""
f = open('yelp_businesses.json', 'rb')
g = open('review_set25000.json', 'rb')
#g = open('review_set.json', 'rb')
cw = open('5k_common_words.csv','rb')

business_data = f.readlines()
review_data = g.readlines()
f.close()
g.close()

# Create array of common stop words
stop_words  = set(['a','able','about','across','after','all','almost','also','am','among','an','and','any','are','as','at','be','because','been','but','by','can','cannot','could','dear','did','do','does','either','else','ever','every','for','from','get','got','had','has','have','he','her','hers','him','his','how','however','i','if','in','into','is','it','its','just','least','let','like','likely','may','me','might','most','must','my','neither','no','nor','not','of','off','often','on','only','or','other','our','own','rather','said','say','says','she','should','since','so','some','than','that','the','their','them','then','there','these','they','this','tis','to','too','twas','us','wants','was','we','were','what','when','where','which','while','who','whom','why','will','with','would','yet','you','your'])

# Create array of 5000 most common English words
common_words = []
for word in cw.readlines():
	word = re.sub(r'\W','', word)
	word = word.lower()
	common_words.append(word)
cw.close()

# Instantiate set for storing business ids
biz_ids = set()
 
# This function looks for businesses that have a category that matches the user input.
def get_reviews(business_data, review_data, category, filename):

    #Open file that will be used to store reviews data
    r = open(filename,'w')

    print('Looking for '+category.lower()+' businesses...')

    #Go through each line and if the category matches the user input add it to the biz_ids set 
    for line in business_data:
        line = json.loads(line)
        if line['type'] == 'business':
            categories = [w.lower() for w in list(line['categories'])]
            if category.lower() in categories:
                biz_ids.add(line['business_id'])        

    #Go through the data again, this time looking for reviews. If the review business id matches an id
    #found in biz_ids, write the line to the text file
    for line in review_data:
        line = json.loads(line)
        if line['type'] == 'review' and line['business_id'] in biz_ids:
            review_words = line['text'].split()

            #Create new array that will replace the existing one found at line['text']
            cleaned_review_words = []

            #Iterate through each word in each review, lower the word, and remove any non-word characters
            for word in review_words:
                word = word.lower()
                word = re.sub(r'\W','', word)
                word = re.sub(r'^[0-9]+$','', word)
                
                #Check to see if the word is either a stop word or a common word. If it is, exclude it
                if word != '' and word not in common_words and word not in stop_words:
                    cleaned_review_words.append(word)

            #Update the line with the new truncated list of words	
            line['text'] = cleaned_review_words

            #Write out the line in JSON format
            r.write(json.dumps(line))
            r.write('\n')
            
    if len(biz_ids)==0:
        return False
    else:
        return True

    r.close()    
        
#Menu that takes user input for category
def menu(resultsFound):

    while resultsFound == False:
        category = raw_input('Type in a business category (e.g. indian, massage): ')
        category = str(category)
        category_str = category.replace(" ", "_").lower()
        filename = "reviews_data." + category_str + ".json"
        resultsFound=get_reviews(business_data,review_data,category,filename)
        
        if resultsFound == False:
            print('No results found for '+ category+ ', please try again: ')
    
    print(str(len(biz_ids))+' businesses found. Your data was output to ' + str(filename))

menu(False)	


	

