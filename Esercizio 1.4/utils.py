import string
import spacy
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.wsd import lesk
from nltk.corpus import wordnet as wn
import matplotlib.pyplot as plt

nlp = spacy.load("en_core_web_sm") #Language object in spacy to do tokenization, ecc., like NLTK
lemmatizer = WordNetLemmatizer()
stop_words = stopwords.words('english')

def read_sentences(file_name):
    "Return: sentences list"
    sents = []

    with open(file_name,'r',encoding="utf-8") as lines:
        for line in lines :
            if len(line.split('<s>')) > 1: # se esistono delle frasi in esso contenute (se esiste del testo dopo il tag <s>)
                sents.append(line.split('<s>')[1].replace('</s>','').strip())
                #inserisco il testo (le frasi contenenti il verbo richiesto),
                #"pulite" dai tag <s> e </s> e spazi a inizio e fine frase
    return sents


def preprocessing(sentence): 
    sentence = [s.lower() for s in sentence] #transformation in lower case
    sentence = [''.join(c for c in s if c not in string.punctuation) for s in sentence] #Remove punctuation

    return sentence


p_subj = {'subj', 'nsubjpass', 'nsubj'}
p_obj = {'pobj', 'dobj', 'obj', 'iobj'}

#parse sentences with spacy to find the subject and the object argument of the selected verb in our sentences
def parse_find_subj_obj(sent, i):
    o = None
    s = None
    
    sent = nlp(sent) #using Language object "en_core_web_sm" with spacy on our sentences

    for elem in sent: #for all the elements of the sentence taken as parameter
            if elem.dep_ in p_subj: #dep_ = "Syntactic dependency relation" -> to find p_subj (verb subject argument in the proposition)
                if elem.lemma_ != "-PRON-": # -PRON- is the default lemma for pronouns in spaCy
                    s = elem.lemma_ #subject found
                else:
                    # This occurs from the issue is that according to creators of spacy; there is no correct meaning of lemmatizing a pronoun;
                    # i.e. turning 'me' into 'I' just isn't sensible enough. while there can be debates on the same aspect;
                    # in spacy every pronoun returns  '-PRON-' on lemmatization.
                    # Therefore, we are checking whether this specific return is coming and if it does,
                    # we just return the token itself instead of the token.lemma_ which doesn't make sense in case of pronouns. 
                    s = elem.text
            if elem.dep_ in p_obj: #dep_ = "Syntactic dependency relation" -> to find p_obj (verb object argument in the proposition)
                if elem.lemma_ != "-PRON-":
                    o = elem.lemma_ #object found
                else:
                    o = elem.text
    parsed_sent(sent)
    return s,o

def parsed_sent(sent):
    psd_sent = []
    psd_sent.append(sent)

def wsd(sent, subj, obj):
    possible_subj = ["i", 'you', 'he', "she", "it", "we", "they"] #soggetti più comuni (pronomi personali) -> riconducibili al super-synset "People"
    if subj in possible_subj: #se il soggetto in questione è di tipo "comune"
        ris = wn.synsets('people')[0]     #Prende il primo synset di WordNet associato al termine 'people'
    elif subj is not None: #se il soggetto in questione non è di tipo "comune" ma è != None -> necessaria analisi ulteriore
    #disambiguazione con algoritmo di lesk (soggetto) -> trova il miglior senso possibile per la parola "subj" nel contesto "sent"
        ris = lesk(sent, subj) 
    else:
        ris = None
    if obj is not None:
    #disambiguazione con algoritmo di lesk (oggetto) -> trova il miglior senso possibile per la parola "obj" nel contesto "sent"
        ris1 = lesk(sent, obj)
    else:
        ris1 = None
    return ris, ris1 #ritorno la tupla (soggetto, oggetto) disambiguata

#Recupero dei supersensi di soggetto e oggetto trovati
def super_sense(ris, ris1):

    if ris is not None or ris1 is not None:
        if ris is not None:
            ss1 = ris.lexname() #lexical category (super-sense) of the subject found
        else: #ris1 is None
            ss1 = None
        if ris1 is not None:
            ss2 = ris1.lexname() #lexical category (super-sense) of the object found
        else: #ris2 is None
            ss2 = None
    else:
        ss1 = None
        ss2 = None

    return ss1, ss2 #return a tuple of possible values (or None) for the super-senses of subject and object

def list_to_string(lista):
    trs = " ".join(lista)
    return trs

def menu(): #scelta del verbo transitivo da analizzare
    print("Scegli il verbo da analizzare inserendo il numero associato")
    print("1 - To Pay;")
    print("2 - To Promise;")