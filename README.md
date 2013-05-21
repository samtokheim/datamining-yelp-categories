#Mining Yelp Reviews to Detect Sub-Categories
-------------------------------------------------------
**Ryan Baker and Sam Tokheim**<br />
May 16, 2013

##Introduction
The problem that we explored in this project is whether or not it is possible to identify potential sub-categories of existing categories by looking at the similarity of words found in Yelp reviews. To explore this possibility, we first created a function to extract reviews of a selected category. We cleaned the review data by removing non-words, stop words and a common words from all relevant Yelp reviews. We then calculated the Jaccard similarity of review word sets between each permutation of Yelp business pair using mrjob, a Python package used for running MapReduce streaming jobs. We then used the resulting matrix of Jaccard coefficients to create clusters of similar businesses by employing an agglomerative technique; this process presented potential sub-categories which defined each cluster. From resulting clusters, we were able to tabulate the most popular words in each cluster, identifying potential names for the new sub-category.

##Problem 
If one types ‘Indian’ food into the Yelp search bar, the first result that appears is ‘Indian food’. But, what if this list also included other Indian categories such as North Indian food, South Indian food, East Indian food, West Indian Food and Indian fusion - just to name a few? This project explores whether or not such groups or clusters of businesses could be identified by using data mining techniques on review text contents in the Yelp Academic dataset.

##Solution
###Getting the data
Before we could begin our analysis, we had to transform the Yelp Academic dataset to meet our needs. Specifically, we created a list of businesses extracted from the full dataset, and a separate list containing a pared-down version of 25,000 reviews - the full list would have been too processor- and time-intensive to work with. From the review text, we removed stop words and 5,000 of the most commonly used words in American English. We did this after our initial testing because we discovered that our clustering algorithm could not identify distinct clusters for our primary test dataset, which included both ‘chinese’ and ‘indian’ restaurants. By reducing the number of common words in each review word set, we were able to make reviews for different types of business more distinguishable from each other.

To transform the data, we created a Python script called ‘get_reviews_data.py’ which receives a category as input from the user. The output of get_reviews_data.py is a JSON document of Yelp reviews called ‘reviews_data.json’ that includes a business id and a list of words: 
**{“business_id”: “IKpwHpcHWvvQmlfX7IgYWg”, "text": ["buffet", "comprised", "samosas", "dosas", "crepes", "starters", "dosas",...]}.**

###Calculating Jaccard similarities
To measure similarity between businesses, we calculated the Jaccard coefficient between the review word sets of each business permutation. In order to generate these Jaccard coefficients, we created a Python script called ‘business_sim.py’ which inputs the JSON document from the previous step, runs a MapReduce job and outputs to a text document called ‘biz_results.[category].txt’. The MapReduce steps are as follows:
	
* Mapper 1: For each word in each review, yield the biz id and word
* Reducer 1:  Outputs business_id as key and a list of unique words as value
* Mapper 2: Outputs a list of business_ids and associated word sets as value
* Reducer 2: Calculates a Jaccard score for each business pair permutation
* Reducer 3: Outputs business_id, business_words array as key and a list of every other business_id and associated Jaccard as the value


###Create clusters
To build up clusters of similar businesses based on the text of their reviews, we used an agglomerative technique in which we initialized a clusters dictionary with each individual businesses being the sole member of its own cluster. Then, we created a recursive function to build up business clusters by merging businesses with their ‘nearest neighbor’ business based on Jaccard similarity. These clusters are built up gradually until a stopping case is satisfied which indicates the presence of two significant clusters. The most prevalent words from reviews in each business cluster are then calculated and displayed.

##Results and future work
We have successfully developed a proof-of-concept for a process of Yelp business sub-categorization through textual data mining. We have implemented a successful test case in which we created a set of reviews, half of which are for Chinese restaurants and half for Indian restaurants. As expected, our process successfully analyzed the text content to assign each business into a cluster representing its natural category (see Figure 1 below). While we were not able to successfully deploy the subcategorization tool for use within categories, this would be achievable with 1) greater computing power, making larger data sets and thus richer word comparisons possible, 2) a stronger implementation of the stopping case, which currently relies on trial-and-error, and 3) greater filtering of common words, including words frequently used in Yelp reviews, from the word sets. With more time, we would be able to implement these changes, and have the chance to experiment with running our program on more interesting and complete data sets.


![Figure 1](/results/results2.jpg)
Figure 1: Resulting word lists after cluster creation using test data. Cluster 170 indicates its mostfrequently seen review words were “naan”, “masala”, and “tikka” clearly indicating Indian restaurants whereas cluster 178 shows “mein” and “dumplings”, associated with Chinese restaurants.

##Related work 
In order to remove commonly used words from the review word sets, we used a list of the 5,000 top words used in the Corpus of Contemporary American English. This list is available for download for free from http://www.wordfrequency.info/. A list of stop words was pulled from http://norm.al/2009/04/14/list-of-english-stop-words/.

##Contact Us
Ryan Baker
* www.linkedin.com/in/ryanfbaker
* www.github.com/flux3000
 
Sam Tokheim
* www.linkedin.com/in/samtokheim
* www.github.com/samtokheim
