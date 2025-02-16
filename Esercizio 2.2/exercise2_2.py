import spacy
import nltk
import random
import pickle
import gensim
import os
import pyLDAvis
import pyLDAvis.gensim_models
import webbrowser
from tqdm import tqdm

path = os.path.dirname(__file__)

from spacy.lang.en import English
from nltk.corpus import wordnet as wn
from gensim import corpora


parser = English()

#clean our text
def tokenize(text): 
    lda_tokens = []
    tokens = parser(text)
    for token in tokens:
        if token.orth_.isspace():
            continue
        else:
            lda_tokens.append(token.lower_)
    return lda_tokens


def get_lemma(word): 
    lemma = wn.morphy(word)
    if lemma is None:
        return word
    else:
        return lemma


en_stop = set(nltk.corpus.stopwords.words('english'))

#function to prepare the text for topic modelling
def prepare_text_for_lda(text): 
    tokens = tokenize(text) #tokenization of words in text
    tokens = [token for token in tokens if len(token) > 4] #take tokens needed to process
    tokens = [token for token in tokens if token not in en_stop] #remove stopwords
    tokens = [get_lemma(token) for token in tokens] #lemmatization
    return tokens

text_data = []

#Open up our data, read line by line
#for each line, prepare text for LDA, then add to a list.
with open(path + '/medium_data-science_1jan2018-31aug2020_tfidf_nmf_10topics.csv') as f: 
    count = 0
    for line in f:                            
        tokens = prepare_text_for_lda(line)
        if random.random() > .99:
            text_data.append(tokens)
        count = count + 1

print (f'Analyzing {count} articles titles..')

#First, we are creating a dictionary from the data, then convert to a bag-of-words corpus 
#and save the dictionary and corpus for future use.
dictionary = corpora.Dictionary(text_data)
# Convert document into the bag-of-words (BoW) format = list of (token_id, token_count) tuples
corpus = [dictionary.doc2bow(text) for text in text_data]
pickle.dump(corpus, open(path + '/result/' + 'corpus.pkl', 'wb'))
dictionary.save(path + '/result/' + 'dictionary.gensim')

#We are asking LDA to find NUM_TOPICS topics in the data
#With LDA, we can see different document with different topics, and the discriminations are obvious
NUM_TOPICS = 10
#gensim.models: contains algorithms for extracting document representations from their raw bag-of-word counts
ldamodel = gensim.models.ldamodel.LdaModel(corpus, num_topics = NUM_TOPICS, id2word=dictionary, passes=15)
ldamodel.save(path + '/result/' + 'model3.gensim') #save for visualization
topics = ldamodel.print_topics(num_words=3) # Get the most significant topics (ordered by significance)
for topic in topics:
    print(topic)


#Visualization:
# pyLDAvis is designed to help users interpret the topics in a topic model that has been fit to a corpus of text data.
# The package extracts information from a fitted LDA topic model to inform an interactive web-based visualization

# Saliency: a measure of how much the term tells you about the topic.

# Relevance: a weighted average of the probability of the word
# given the topic and the word given the topic normalized by the probability of the topic.

# The size of the bubble measures the importance of the topics, relative to the data.

# When we have 5 or 10 topics, we can see certain topics are clustered together,
# this indicates the similarity between topics

#transform and prepare a LDA model's data for visualization
vis_data = pyLDAvis.gensim_models.prepare(ldamodel, corpus, dictionary)
pyLDAvis.save_html(vis_data, path + '/result/' + str(NUM_TOPICS) +'.html')
#absolute path below (modify if needed!)
webbrowser.open("file:///Users/itsallmacman/Downloads/TLN3_Maltese_Morelli/Esercizio 2.2/result/" + str(NUM_TOPICS) + ".html")
#(path + "/result/" + str(NUM_TOPICS) + ".html") #relative path not working with webbroser.open()
#"file:///Users/itsallmacman/Downloads/TLN3_Maltese_Morelli/Esercizio 2.2/result/" + str(NUM_TOPICS) + ".html"