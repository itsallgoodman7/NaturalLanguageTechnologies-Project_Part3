import csv
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from collections import Counter
from collections import defaultdict
from prettytable import PrettyTable
import os

path_ = os.path.dirname(__file__)

#all the correct concepts, used for writing the results (def getTableResult(c1,c2,c3,c4))
correct_terms = ["courage", "paper", "apprehension", "sharpener"] 

"""
Load a csv file
Input:
    path: file path
Output:
    dataset: dictionary in this form: {'Concetto 1': [definitions]... 'Concetto n': [definitions]}
"""
def loadCsv(path):
     with open(path, "r", encoding="utf-8") as definitions:
        reader = csv.reader(definitions, delimiter=',')
        #creation of 4 lists to contain all the definitions of each of the 4 terms
        def_abstract_generic = []
        def_concrete_generic = []
        def_abstract_specific = []
        def_concrete_specific = []

        first = True
        for line in reader: #for all the rows...
            if not first: #...take the 2nd/3rd/4th/5th column and insert its data in the appropriate list
                def_abstract_generic.append(line[1])
                def_concrete_generic.append(line[2])
                def_abstract_specific.append(line[3])
                def_concrete_specific.append(line[4])
            else:
                first = False
        
        #creation of a python dictionary to store all the values collected for the 4 terms {1: [list_of_defs1], 2: [list_of_defs2], ...}
        dictionary = {}
        dictionary[0] = def_abstract_generic
        dictionary[1] = def_concrete_generic
        dictionary[2] = def_abstract_specific
        dictionary[3] = def_concrete_specific


        return dictionary                           
"""
Preprocess a list of sentence
Input:
    definitions: list of sentence
Output:
    processed: list of words (no punct, no stop words)
"""
def preProcess(definitions):
    sentences = [d for d in definitions if d != '']
    processed = []
    for s in sentences:
        processed.extend(bagOfWords(s))
    return processed

#method that process a (single) sentence removing stopwords, punctuation and doing lemmatization
def bagOfWords(sentence):
    stop_words = set(stopwords.words('english'))
    punct = {',', ';', '.', '(', ')', '{', '}', ':', '?', '!', "''", "something"}
    lemmatizer = nltk.WordNetLemmatizer()
    tokens = nltk.word_tokenize(sentence.lower()) #tokenization of the sentence (in lower case)
    tokens = filter(lambda x: x not in stop_words and x not in punct, tokens) #remove stopwords and punctuation
    #doing lemmatizations of the "cleaned" tokens, and returning a list of the results
    return list((lemmatizer.lemmatize(w) for w in tokens))
    
"""
Order a list of definitions by the most common words
Input:
    list_of_defs: list of definitions
Output:
    list of definitions processed (preProcess/bagOfWords) and sorted by the most common words
"""
def getCommonWords(list_of_defs):
    #Counter: Dict subclass for counting hashable items.
    #Elements are stored as dictionary keys and their counts are stored as dictionary values.
    words = Counter(preProcess(list_of_defs)) #counting the frequency of each word in the input definitions, after doing preprocess
    #sorting (using the dict values = word counts) the most commond words in the definitions
    #(the words with the highest frequency) in descending order
    common_words = sorted(words, key=words.get, reverse=True)
    return common_words

#write a table on a file
def writeTable(table, path):
    data = table.get_string() #convert table data into string
    #printing out (into the shell) the PrettyTable results:
    #(Correct Concept", "(best 1) Authomatic Concept", "Definition") in a string format
    print(data)
    print("Result output also foundable at this path: " + path + "\n")
    with open(path, 'w') as f:
        f.write(data) #writing the output results into the file ("bestConcepts.txt")

"""
Write in a table the correct concepts, the authomatic concepts found and the corrispective definitions
Input: 
    c1,...c4 = lists of synsets sorted by the higher overlap with the given definitions
Output:
    res =  PrettyTable
"""
def getTableResult(c1, c2, c3, c4):
    
    res = PrettyTable()
    res.field_names = ["Correct Concept", "Best WordNet Synset Found", "Definition"]
    #(correct_terms are all the correct starting concepts)

    #storing each time in a new row of the table "res":
    # the correct concept, the best (1) synset retrieved and the gloss associated to that WN synset 
    res.add_row([correct_terms[0], c1[0].name(), c1[0].definition()])
    res.add_row([correct_terms[1], c2[0].name(), c2[0].definition()])
    res.add_row([correct_terms[2], c3[0].name(), c3[0].definition()])
    res.add_row([correct_terms[3], c4[0].name(), c4[0].definition()])
    return res  #returning the PrettyTable containing, for each of the 4 starting concepts:
                #"Correct Concept", "(best 1) Authomatic Concept", "Definition"

#write all the found concepts on a file
def writeResults(c1, c2, c3, c4):
    result_list = [c1, c2, c3, c4]
    with open(path_ + "/output/allFoundConcepts.txt", "a") as a_file:
        ind = 0
        for term in correct_terms: #(correct_terms are all the correct starting concepts)
            a_file.write(term)
            a_file.write("\n")
            #writing into the file ("allFoundConcepts.txt"), for all the correct_terms (the 4 starting concepts),
            #all the informations found = all the 10 WN synsets retrieved automatically
            #(the best 10 ones, according to the overlap results)
            a_file.write(str(result_list[ind]))
            a_file.write("\n") #making space for the next concept...
            a_file.write("\n")
            ind += 1

"""
Return a list of synset, related to a concept. The list contains the synset of every
common word, its hypernyms and its hyponyms ->
sorted by the overlaps computed with the context (the complete list of definitions) 
(list[0] will be the most probable sense, having the highest overlap with the context).
Input: 
    common_words = lists of the 3 most common words in the definition
    context = list of processed words from the definitions of every concept
Output:
    overlaps_list =  list of synset sorted by the overlaps with the context
"""
def getConcepts (common_words, context):
    #list of all the best synsets retrieved (from the most commond word 
    #(used as hyperonim/genus of the term to identify) and its hyponims)
    #to compare with the terms in the context (the complete list of the definition considered)
    overlaps_list = []

    #studying 3 the most common words used in the definition:
    #and using them as "potential genus" / hypernomim of the term (and relative WN synset) to identify 
    # (ex: Apple -> fruit)
    # -> identify "Apple" (its correctly intended WN synset) by taking its hyperonim "fruit" and searching, among its hyponims,
    # which best fits with the context (which hyponim of fruit has the most similar context to the global one's)

    for genus in common_words: #for all 3 of the most commond words of a definition
        #best_sense = lesk(context, genus)
        #hypo_list = best_sense.hyponyms()
        hypo_list = getAllHyponyms(genus)
        overlaps_list.extend(getSynsetsOverlap(hypo_list, context)) #computing a list of tuples (synset, overlap)...
    overlaps_list.sort(key=lambda tup: tup[1], reverse=True) #...and sorting it (by the value of the overlap) by descending order
    #taking only the first elem (the WN synset of a certain hyponim of the genus) of the tuples (synset, overlap) in overlaps_list
    overlaps_list = [a_tuple[0] for a_tuple in overlaps_list]

    #returning only the first 10 synsets (the 10 hyponyms with the most similar context with the global context for the def considered)
    return overlaps_list[:10]


#get all the WordNet hyponyms (synsets) of the input genus (the hyperonim considered)
def getAllHyponyms(word):
    hypo_list = []
    for ss in wn.synsets(word): #for all the WN synsets of the word (the input genus)
        hypo_list.extend(ss.hyponyms()) #extend the hyponim list with all the WN hyponim synsets retrieved
    return hypo_list

def getSynsetsOverlap(synsets, context):
    """
    Create a list of tuples that contains all the synsets and the corrispective overlap with the given context
    Input: 
        synsets = lists of synsets (of all the hyponims retrieved from the genus/hyperonim considered)
        context = list of processed words from the definitions of every concept
    Output:
        best_synsets =  list of tuples in the form : [(synset 1, overlap 1),...(synset n, overlap n)]
    """
    best_synsets = []
    for syn in synsets: #for each of the hyponim synsets passed as parameters
        syn_context = getSynsetContext(syn)
        #comparing the context of a given hyponim synset and the global context (of the complete list of the processed definition)
        overlap = len(set(syn_context) & set(context))
        best_synsets.append((syn, overlap))        
    return best_synsets # list of tuples (synset, overlap)

#get the context of a synset (formed by its definition and its examples) in a bag-of-word approach
def getSynsetContext(s):
    context = bagOfWords(s.definition())
    for e in s.examples():
        context=list(set().union(context, bagOfWords(e)))
    return context