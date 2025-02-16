import csv
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
import numpy as np
import pandas as pd
import os

from collections import Counter


path = os.path.dirname(__file__)


def load_data():
    """
    It reads the CSV definitions file for the four terms
    :return: four list containing the read definitions.
    """
    with open(path + config["input"], "r", encoding="utf-8") as definitions:
        reader = csv.reader(definitions, delimiter=',')

        def_abstract_generic = [] #courage
        def_concrete_generic = [] #paper
        def_abstract_specific = [] #apprehension
        def_concrete_specific = [] #sharpener

        first = True
        for line in reader:
            if not first:
                #inserting the right definitions in the right list
                def_abstract_generic.append(line[1])
                def_concrete_generic.append(line[2])
                def_abstract_specific.append(line[3])
                def_concrete_specific.append(line[4])
            else:
                first = False #skipping the first line (=doc legend)

        return def_abstract_generic, def_concrete_generic, def_abstract_specific, def_concrete_specific


def bag_of_words(definition):
    """
    It does some preprocess: removes the stopword, punctuation and does the
    lemmatization of the tokens inside the sentence.
    :param definition: a string representing a definition
    :return: a set of string which contains the preprocessed string tokens.
    """

    # Removing stopwords
    definition = definition.lower()
    stop_words = set(stopwords.words('english'))
    punct = {',', ';', '(', ')', '{', '}', ':', '?', '!', '.'}
    wnl = nltk.WordNetLemmatizer()
    tokens = nltk.word_tokenize(definition)
    tokens = list(
        filter(lambda x: x not in stop_words and x not in punct, tokens)) #returning only the "clean" tokens

    # Lemmatization
    lemmatized_tokens = set(wnl.lemmatize(t) for t in tokens) #lemmatization of the "clean" tokens returned

    return lemmatized_tokens #set of lemmas (cleaned after preprocessing)


def compute_overlap_terms(definitions):
    """
    It computes the overlap between two set of the preprocessed terms (all the combinations)
    :param definitions: a list of definitions (strings)
    :return: a list containing the similarity score (overlap) of each definition.
    """

    results = [] #task 1.1 - similarity score (within the definitions)
    frequency = [] #task 1.2 - similar words frequency (within the definitions)
    
    i = 0
    while i < len(definitions):
        a = bag_of_words(definitions[i])  # set of terms (after preprocessing) of the first definition
        j = i + 1
        while j < len(definitions) - 1:
            b = bag_of_words(definitions[j])  # set of terms of the second definition
            # Computing similarity between definitions
            t = len(a & b) / min(len(a), len(b)) # overlap result with normalization [0,1]
            results.append(t) #inserting overlap results in list result
            j = j + 1
        frequency += list(a) #storing all the lemmatized_tokens within each list
        i = i + 1

    return results,frequency

if __name__ == "__main__":

    config = {
        "input": "/input/defs.csv"
    }


    defs = load_data()  # Loading the defs.csv file

    count = 0
    first_row = []  # generic abstract, generic concrete
    second_row = []  # specific abstract, specific concrete

    percentage = ["generic_abstract","generic_concrete", "specific_abstract", "specific_concrete"]

    counter = [] #list for storing the most common words for each term definitions

    for d in defs: #for each of the four list containing the read definitions

        # computing the mean of the overlap of the definitions
        overlap_terms, frequency = compute_overlap_terms(d)
        mean_terms = np.mean(overlap_terms)

        # filling the rows of the matrix to print out similarity results
        if count == 0:
            first_row.append('{:.0%}'.format(mean_terms))
        elif count == 1:
            first_row.append('{:.0%}'.format(mean_terms))
        elif count == 2:
            second_row.append('{:.0%}'.format(mean_terms))
        else:
            second_row.append('{:.0%}'.format(mean_terms))
            
        count += 1

        #ex.1.2 (frequency rate of the 3 most similar words for each of the 4 term definitions)
        counts = Counter(frequency) #counting the most frequent terms of each term definitions (all stored in frequency)
        counter.append([(i, str(round((counts[i] / len(d) * 100.0),2)) + '%')   for i, count in counts.most_common(3)]) #3 most common words for every term definitions [ with relative frequency(%) ]

    # build and print dataframe
    df_similarity = pd.DataFrame([first_row, second_row], columns=["Abstract", "Concrete"],
                               index=["Generic", "Specific"])

    print("\nEsercizio 1.1 - Similarità:\n")
    print(df_similarity)
    
    print("\n\nEsercizio 1.2 - Similarity Explanation:\n")
    for index,key in enumerate(percentage):
        print(f'most frequent words for {key} = {counter[index]}')