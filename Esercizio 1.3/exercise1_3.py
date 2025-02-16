import csv
import os
import pandas as pd
import nltk 
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords

path = os.path.dirname(__file__)

import csv

def aux(sent): #preprocessing (tokenization and stopword removal)
    stop_words = set(stopwords.words('english'))
    tokens = nltk.word_tokenize(sent)
    tokens = list(filter(lambda x:  x not in stop_words, tokens))
    return set(tokens)

def wn_definitions(word):
    word_senses = wn.synsets(word) #taking wordnet synsets of the given parameter "word" 
    wn_definition = set() #list for storing lexical category and relative definitions
    # Synset('noun.animal.01') (= word_senses[0]) -> noun.animal (= lexname) -> animal (= .split('.')[1])
    lexical_category = word_senses[0].lexname().split('.')[1] #from word=dog to hypernomim=animal
    wn_definition.add(lexical_category) #adding hyperonim (lexical category of the term "word" in WordNet)
    #print (wn_definition)
    for sense in word_senses:
        #adding preprocessed hyperonims glosses (cleaned ex. "zebra" tokens of the definitions)
        wn_definition.update(aux(sense.definition()))
    #print (wn_definition)
    return wn_definition

def intersection(word):
    "Return: intersection beetween word's features in PropertyNorms and WN definitions "
    return (words.get(word) & wn_definitions(word))


#execution start
words = dict()
words_not_aux = dict()

#transforming the csv file (PropertyNorms) in python dictionaries {concept: [features]} for our own comodity
with open(path + '/property_norms_cut.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter = ';')
    for row in reader: # for each line read from the csv file
        #fill "words" dict keys with all the concepts from the column "concept", for each line read
        words[row['concept']] = set() #set to contain all the processed features (= dict values) of a certain concept (= dict key)
        words_not_aux[row['concept']] = [] #equal to dict words but not using preprocessing (def "aux(sent)")

with open(path + '/property_norms_cut.csv') as csvfile:
    reader = csv.DictReader(csvfile, delimiter = ';')
    for row in reader:
        #fill "words" dict values with informations from the column "feature" of the retrieved concept
        words.get(row['concept']).update(aux(row['feature'])) #adding preprocessed values (features) to the relative retrieved key (concept)
        words_not_aux.get(row['concept']).append((row['feature'])) #adding not preprocessed values (features) to the relative retrieved key (concept)

var = input("Please enter a word: ")
#compute intersection between PropertyNorms features
#and WordNet informations retrieved for the word written 
present = intersection(var) # printing out the features (for the given concept) present both in PropertyNorms (csv) and in WordNet
print(present)

with open(path + '/result.csv', 'w') as csv_file:  
    writer = csv.writer(csv_file)
    writer.writerow(['Concept', 'Feature', 'Present_in_WN'])
    # input string "var" must be one of the concepts present in the csv (PropertyNorms) file

    #for all the values relative to the given concept (key of the dict)
    for value in words.get(var): #using dictonary without (words_not_aux) / with pre-processing (words)
        if (set(value.split())) & present: #if this feature in among the features present in both resources
            writer.writerow([var, value, 'yes'])
        else: # in this features in not present in both resources
            writer.writerow([var, value, 'no'])


