import fileinput
import csv
import json

businesses = {} # will store the business_id, its word set, and business comparisons
clusters = {} # will store a cluster id, with the array of business_ids that are in the cluster

def getBusinessList(filename):
    try:
        f = open(filename, "rb")
        for line in f.readlines():
            key, value = line.split("\t", 1)
            biz_info = json.loads(key)
            biz_comps = json.loads(value)
            biz_id = biz_info[0]
            biz_words = biz_info[1]
            
            businesses[biz_id] = {'business_words': biz_words, 'business_comps': biz_comps}

        f.close()
        return businesses
    except IOError:
        return False

def getClusters(businesses):   
    
    count = 0
    for i, v in businesses.iteritems():
        business_id = str(i)
        """ 
        This cluster dictionary will start out with each business as the sole member of its own cluster. Then, through agglomeration the clusters will be merged to their nearest neighbors. Merging will stop when a certain number of clusters remain, or when the jaccard distance between two clusters' nearest neighbors fall below a certain threshold.
        """    
        clusters[count] = {'cluster_id': count, 'cluster_businesses': [business_id]}        
        count = count + 1
    return clusters
    
def agglomClusters(clusters, coefficient, iterCount=1):

    """
    This is the recursive formula to build up membership in each cluster by merging them with each other based on similarity.

    Pseudocode:
    
    if len(clusters) reaches a certain length, or other stop case,
        return clusters
    
    else:    
        for each cluster c:
            cluster_max_jaccards = []
            for each business b in the cluster:
                max_jaccards = []
                find the business k in any other cluster that has the highest jaccard to business b (this will utilize the businesses dictionary)
                    append (business_id, jaccard, cluster_id) of business k to max_jaccards
                after filling up max_jaccards, find the max of all the jaccards. (this will represent the closest neighbor to any point in the cluster)
                append cluster_max_jaccards with (cluster_id, max_jaccard)
                
            get the cluster_id that has the highest max_jaccard in cluster_max_jaccards
        
        do the same max jaccard test for all points in all clusters. find the highest-jaccard pair in the whole data set.
        merge cluster 1 into cluster 2, by appending cluster1['cluster_businesses'] with cluster2['cluster_businesses'].
        del cluster 2
                        
        we now have a new clusters dictionary - call recursive formula
        return agglomClusters(clusters)
    
    """

    cluster_len = len(clusters)

    tokheim_baker_coefficient = float(coefficient) # this is the critial tokheim-baker coefficient.
    
    """
    The tokheim-baker coefficient:
    
    Cluster formation will stop when two clusters have this ratio of total businesses in their cluster. For instance, if there are 100 total 
    businesses, and we set a coefficient of 0.33, recursion will stop when two clusters have at least 33 businesses in them. This is
    a critical coefficient to get right so that underclustering and overclustering do not occur. 
    
    A low coefficient means the expected segmentability of the businesses set is low. Use a low coefficient when clear delineations are not expected.
    
    A high coefficient means the expected segmentability is high. If you anticipate two clear clusters to emerge, use a higher coefficient.
    
    In general, start low, then increase. Maximum is 0.5.    
    
    """

    target_cluster_size = cluster_len * tokheim_baker_coefficient
    
    max_cluster_size = cluster_len * .90 
        
    # stop case 1: if one cluster has reached more than 3/4 the size of the data set, stop the recursion. we are probably just gonna end up with one cluster.    
    # stop case 2: if two clusters have the requisite number of businesses in them, as determined by the t-b coefficient, stop the agglomeration.
    
    for cluster1, value1 in clusters.iteritems():
        cluster1_businesses = list(value1['cluster_businesses'])
        cluster1_id = value1['cluster_id']
        
        if len(cluster1_businesses) >= max_cluster_size:
            return cluster1_id, cluster1_businesses, '', ''
            
    for cluster1, value1 in clusters.iteritems():
        cluster1_businesses = list(value1['cluster_businesses'])
        cluster1_id = value1['cluster_id']
        
        if len(cluster1_businesses) >= max_cluster_size:
            return cluster1_id, cluster1_businesses, '', ''    
        if len(cluster1_businesses) >= target_cluster_size:
            for cluster2, value2 in clusters.iteritems():
                if cluster2 != cluster1:
                    cluster2_businesses = list(value2['cluster_businesses'])
                    cluster2_id = value2['cluster_id']
                    if len(cluster2_businesses) >= target_cluster_size:
                        return cluster1_id, cluster1_businesses, cluster2_id, cluster2_businesses
                        
    else:
        print "\n"
        print "Processing next iteration...."
        print "\n"       
        total_max_jaccards = [] # [jaccard coeff, cluster 1, cluster 2]
        for c, v in clusters.iteritems():
            #print '\n{0}\nCLUSTER {1}\n{0}\n'.format('#'*70, c)    
            
            cluster_max_jaccards = []
            c_businesses = list(v['cluster_businesses'])
            biz_count = 1
            for this_business in c_businesses:
                # this_business is the key, which is the business_id                
                max_jaccards = []                
                """
                1. find the business x in any other cluster that has the highest jaccard to business b (this will utilize the businesses dictionary)
                2. append (jaccard_coeff, jaccard_biz, jaccard_cluster) of business x to max_jaccards
                """
                                
                this_business_info = businesses[this_business]
                this_business_comps = list(this_business_info['business_comps'])
                
                #print '\n{0}\n Similarities for Business {2}: {1}\n{0}\n[jaccard_coeff, business_id, cluster_id]\n\n'.format('-'*70, this_business, biz_count)
                
                for foo_business in this_business_comps: # get all the [business_comp_ids, jaccards] for this business
                    this_max_jaccard_coeff = 0
                    this_max_jaccard_biz = ''
                    this_max_jaccard_cluster = ''
                    
                    if foo_business[0] not in c_businesses: # this business is in a different cluster than c. ok to proceed.
                        if foo_business[1] > this_max_jaccard_coeff:
                            this_max_jaccard_coeff = foo_business[1] # set the current jaccard to the max, it's the largest we've seen.                        
                            this_max_jaccard_biz = foo_business[0] 
                        
                    # find the cluster the max_jaccard business is in
                    for cc, vv in clusters.iteritems():
                        cc_businesses = list(vv['cluster_businesses'])
                        if this_max_jaccard_biz in cc_businesses:
                            this_max_jaccard_cluster = vv['cluster_id']
                        
                    max_jaccards.append([this_max_jaccard_coeff, this_max_jaccard_biz, this_max_jaccard_cluster])
                    max_jaccards_sorted = sorted(max_jaccards, reverse=True)

                #after filling up max_jaccards, find the max of all these jaccards. (this will represent the closest neighbor to any point in the cluster)
                max_jaccard = max(sorted(max_jaccards))
                
                this_business_max_jaccard_coeff = max_jaccard[0]
                this_business_max_jaccard_cluster = max_jaccard[2]
                
                #print '\n{0}\nCluster {4} Business {3} - {2} - Maximum similarity:\n{1}\n{0}\n'.format('-'*70, max_jaccard, this_business, biz_count, c)

                #append cluster_max_jaccards with (this_max_jaccard_coeff, this_max_jaccard_cluster)
                
                cluster_max_jaccards.append([this_business_max_jaccard_coeff, this_business_max_jaccard_cluster])
            
                biz_count = biz_count + 1
                
            cluster_max_jaccards = sorted(cluster_max_jaccards)
            top_cluster_similarity = max(cluster_max_jaccards)
            
            #print '{0}\nArray of max jaccards in cluster {2} businesses:\n{1}\n{0}\n'.format('-'*70, cluster_max_jaccards, c)
            #print '{0}\nNearest neighbor cluster to cluster {2}: \n{1}\n{0}\n'.format('-'*70, top_cluster_similarity, c)
        
            total_max_jaccards.append([top_cluster_similarity[0], c, top_cluster_similarity[1]]) # [jaccard coeff, cluster 1, cluster 2]
        
        """
        1. get the cluster_id q that has the highest jaccard value in total_max_jaccards
        2. merge cluster q into cluster c, by appending c['cluster_businesses'] with q['cluster_businesses'].
        3. del cluster q
        """
        
        total_max_jaccards = sorted(total_max_jaccards)
        most_similar_clusters = max(total_max_jaccards)            

        the_winning_jaccard = most_similar_clusters[0]
        cluster1 = clusters[most_similar_clusters[1]]
        cluster2 = clusters[most_similar_clusters[2]]
        cluster1_id = cluster1['cluster_id']
        cluster2_id = cluster2['cluster_id']
        cluster1_businesses = cluster1['cluster_businesses']
        cluster2_businesses = cluster2['cluster_businesses']

        print "\n"
        print '-'*70
        print "ITERATION %s" % iterCount
        print '-'*70
        
        for b2 in cluster2_businesses:
            cluster1_businesses.append(b2)
            
        del clusters[cluster2_id]
        print '\n{0}\nNEW CLUSTERS:\n{0}\n'.format('-'*70)
        for cl, vl in clusters.iteritems():
            print 'Cluster {0} - Businesses: {1}\n'.format(cl, vl['cluster_businesses'])

        print '-'*70
        print "ITERATION %s COMPLETE" % iterCount
        print '-'*70
        print "OVERALL MAXIMUM JACCARD IS %s" % the_winning_jaccard
        #print "CLUSTER ONE ID: %s" % cluster1_id
        #print "CLUSTER TWO ID: %s" % cluster2_id
        #print "CLUSTER ONE BUSINESSES: %s" % cluster1_businesses
        #print "CLUSTER TWO BUSINESSES: %s" % cluster2_businesses

        #we now have a new clusters dictionary - recurse function
        
        return agglomClusters(clusters, coefficient, iterCount+1)
                

def compareWords(cluster1_id, cluster1_businesses, cluster2_id, cluster2_businesses, businessess):

    # create total word lists for each business, check businesses{} for the words, append to a master set.

    cluster1_words = []
    cluster2_words = []

    # SAMPLE CLUSTERS - CLUSTER 1 = INDIAN, CLUSTER 2 = CHINESE
    
    #cluster1_businesses = ['_jg2zJPu7iNI0Ct0XNN3YQ', 'hCnQgU5GyG3yWGiwLMHCzA', 'FJlMfEtr7E-uTzUxspuzIg', '3fV1JsA8tkhULXAT4O3-_w', 'TqL0ytKAucWdW2mR7EbayA', '4KBLVr3PYilTUUWj3DWwVw', 'QfpwAp53h_DIfzph0IMIbQ', 'TKDgFp9C7kf_pSHrQHZW_Q', 'xtyK6kDA4A2ASCVuU2vH7A', 'ou0vKXhcA6SlOUS4Io3LpQ', '_--ScmaNumIoT2gQanACvg', 'INaAXfbIXtXTB3sSDX8Wow', 'KK-6rXbIo9B4-b_P5WO5Qg', 'XjHwaC53U_xSyAL5-APIVw', 'YN4Kk751tmdvoarGo8z7_A', 'Y2I946V78wOdwaUD9chmqg', '3FB30LGJfWUKxRqwXfq9UQ', 'W_GBVQipa5JnIYbTkKdlRg', '-t6JanEk_V6VzctlTyr6eA', 'zxSfGIhK3hH3vVz_pS5eaA', '778QRHfyHcW7PkEK2OxdrQ', 'RWD95WS_ViX5PE7idDICBQ', '2bw-jWCirbgcUQovqzlf3Q', 'mbPyoVGKB99RHaycV_mPwQ', 'mAKL2FYbfsQgR0g_MhqnsQ', 'uvj_tGQrGDSVXjNU4pHjCA', 'kkgAgHRZ4T7dEJDlNy2CYg', 'RMSSpyOX7rEAjUoKI4Svqg', 'g6NXfYp1ZeJjUQrqne8-Ig', 'N1ZXhAVzOzbyCBPEXTaUUw', 'THPDeKwowt8XZuUcIgtzjQ', 'mhZL8QyPjuqUWePU1oPuEA', '2C_ggj_PARSy6a-qnqEkrA', 'qtyNbCXut-RQnnEQNJ9UzA', 'VZNKj35pKzs-fR8_CMPrgA', 'Ee7h-Pp4jhAEQVK7ay2AtQ', 'PyTHy9VPOhBCiGLsi-PA2Q', '9OhPfV0C3Q49l5tSre2MuQ', '0gE8y94ytFFdFDDNon-K0g', 'L9S4WSPE3r1Bg9KgIlTqpA', '5Dy9fuSYcd4E3XGQRZzOTA', 'AsgtzyqpdjuPyjaEUVcUXA', '92727MDUGRemJ4hvN-hG1g', '7zDbcbUkafhkanpTE5TQRQ', 'yizsyT2dq-Bv8X7bBn5fHA', 'lORvOUQWdp8DsCAFfTEWow', 'hlSh6K0idX0QWH-1Be2N5Q', 'SmLJWc73PcL3gox-LiVAaQ', 'KgfFn5Z51DZoUzhJ186a0A', 'WmEsbfEJn5WZ0D8dViYT8w', 'AqyDXaob6pF7zE2s9nFR2w', 'XyCYPxeZd54UWgIFXsjtgw', 'NtyjXKWUH_Lc0XEbxhp_1g', 'K3EBuyhTBTAhR2-ImlrtJg']

    #cluster2_businesses = ['7TStzQMNtPQIBNaIYcZ_zw', 'r8onTb0QC4lDqLbGsgQrgg', 'DOeyLO90LxcnAjZxK-s9HA', 'sKyz9G6_LHGUAV5jRraCuw', 'XyeRCD7AAkwzPL8stT_Law', '_mv3DhRD3L3okFXYjxX_Cg', 'y1Bw86Rv98bDYoH4ICDSgg', 'xULATz2siGXOPia614mg2A', 'sPd-zQtPSARMw1vx131v1w', 's_TqvH0o3AQCOgTdp2rSmQ', 'WWyaK9oskNOpjCsO6MA7Pw', 'MBirSnTW4pt2k7Ny6KC72w', 'm6mUVUdkGuicmQHuqJH9yw', 'RHEn-QF2RBAcLhzLfpHLiQ', 'uh1SSWqq0-IV_BY78Lpz_Q', 'GUoVncYpFzfxt2HJZFBqDw', 'aLE4Lg5uOGnewTTweXJNBw', 'XODz0rilGYo6_xd5e7isOw', 'ts5aB7jIh-6KBrshG0Lhxw', '6CruOxyuBRnJJx3wRu_oMA', 'wIhtFlx1DdDvYH0fjUAtkg', 'Qzb72EJsUwwpxXOMx_DOYA', 'oiAeXIRf5Q0p1dPH2nziug', 'G5OTROd4bYoLn478GteRZA', '5OY43DZbO-IwYSQ91yRyPw', '-865Ps6xb3h1LP67JcQ3mA', '8Xq5VtwYjayKlxEY2PipQA', '-6ncX3fnQ9OLCjfiUe-kFg', '5qtc1s-TKdgzPccKwY4SRw', '-CRjqZ4GxZ6lIa_qMj7-yw', 'jsUTsVpjI5QPtPfaciENHg', '7aZf5c1UNotq4MabBXMZLA', 'njngMI0mhAGJ-kH0oo68Ow', 'EFWtz7tkjqBebrX7YUly_Q']
    

    for cluster_business_id in cluster1_businesses:
        business_dict = businesses[cluster_business_id]
        business_words = business_dict['business_words']
        for word in business_words:
            cluster1_words.append(word)

    cluster1_words = sorted(cluster1_words)    
    
    for cluster_business_id in cluster2_businesses:
        business_dict = businesses[cluster_business_id]
        business_words = business_dict['business_words']    
        for word in business_words:
            cluster2_words.append(word)

    cluster2_words = sorted(cluster2_words)

    from collections import Counter
    print '\n{0}\n{0}\nCLUSTERING RESULTS\n{0}\n{0}\n'.format('#'*70)
    print "TWO CLUSTERS HAVE BEEN IDENTIFIED: {0} AND {1}".format(cluster1_id, cluster2_id)     
    
    words_to_count1 = (word for word in cluster1_words if word not in cluster2_words)
    #words_to_count1 = cluster1_words
        
    c = Counter(words_to_count1)
    most_common = c.most_common(10)
    print '\n{0}\nMOST COMMON WORDS UNIQUE TO CLUSTER {1}:\n{0}\n'.format('-'*70, cluster1_id)
    print('{:15} {:4}'.format('WORD','COUNT'))    
    print('{:15} {:4}'.format('-'*15,'-'*15))      
    for e in most_common:
        #print e[0], e[1]
  
        print('{:15} {:2}'.format(e[0],e[1]))    

    words_to_count2 = (word for word in cluster2_words if word not in cluster1_words)
    #words_to_count2 = cluster2_words
    
    d = Counter(words_to_count2)
    most_common = d.most_common(10)    
    print '\n{0}\nMOST COMMON WORDS UNIQUE TO CLUSTER {1}:\n{0}\n'.format('-'*70, cluster2_id)
    print('{:15} {:4}'.format('WORD','COUNT'))    
    print('{:15} {:4}'.format('-'*15,'-'*15))     

    
    for e in most_common:
        #print e[0], e[1]
        print('{:15} {:2}'.format(e[0], e[1]))    
        

#Menu that takes user input for filename to process
def menu(businesses):
    while businesses == False:
    
        filename = raw_input('Enter filename to process (e.g. biz_results.indian.txt): ')
        filename = str(filename)

        
        businesses = getBusinessList(filename)
        
        if businesses == False:
            print('No file found named '+ filename+ ', please try again: ')  
    
menu(False)	
    
clusters = getClusters(businesses)
        
print "\n"
print "The Tokheim-Baker Coefficient determines at which cluster size the agglomeration will stop. When two clusters reach a certain percentage of the total size of the business list, as determined by this coefficient, the results will be returned. For example, for a set of 100 businesses and a coefficient of .33, the recursion will end when two clusters each have 33 or more businesses."
print "\n"
print "This is a value between 0 and 0.5. Good to start lower, around .15, and go upwards. Too high a value will result in overclustering, too low will result in underclustering."
print "\n"
coefficient = raw_input('Enter the Tokheim-Baker Coefficient: ')

cluster1_id, cluster1_businesses, cluster2_id, cluster2_businesses = agglomClusters(clusters, coefficient)        

if cluster2_id == '':
    print '\n{0}\n{0}\nCLUSTERING RESULTS\n{0}\n{0}\n'.format('#'*70)
    
    print "Bummer, no distinct clusters emerged. This happened because no significant differences were found between the word sets of each business.\n" 
    print "Consider reducing your coefficient to a value lower than", str(coefficient), "or removing more common words from the word sets.\n\n"
    print "The resulting large cluster was: {0}".format(cluster1_businesses)

    # Just for the heck of it, print out the most common words in the cluster.
    cluster1_words = []
    for cluster_business_id in cluster1_businesses:
        business_dict = businesses[cluster_business_id]
        business_words = business_dict['business_words']
        for word in business_words:
            cluster1_words.append(word)

    cluster1_words = sorted(cluster1_words)    
    words_to_count1 = (word for word in cluster1_words)
    #words_to_count1 = cluster1_words
    from collections import Counter    
    c = Counter(words_to_count1)
    most_common = c.most_common(10)
    print '\n{0}\nMOST COMMON WORDS IN THE CLUSTER:\n{0}\n'.format('-'*70, cluster1_id)
    print('{:15} {:4}'.format('WORD','COUNT'))    
    print('{:15} {:4}'.format('-'*15,'-'*15))      
    for e in most_common:
        #print e[0], e[1]
  
        print('{:15} {:2}'.format(e[0],e[1]))        
    
else:    
    compareWords(cluster1_id, cluster1_businesses, cluster2_id, cluster2_businesses, businesses)
      
