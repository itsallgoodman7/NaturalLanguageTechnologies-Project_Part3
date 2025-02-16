from collections import Counter
import matplotlib.pyplot as plt
from utils import *
import os
from tqdm import tqdm


path = os.path.dirname(__file__)

if __name__ == '__main__':

    menu()
    file_name = ''
    verb = int(input())
    if verb != 1 and verb != 2:
        print("Valore non corretto. Inserisci 1 or 2")
    elif verb == 1:
        file_name = path + "/Corpus/payfilter.txt" #selezione del verbo "Pay"
    else:
        file_name = path + "/Corpus/promise.txt" #selezione del verbo "Promise"

    frasi = read_sentences(file_name) #lettura di istanze di utilizzo del verbo selezionato (nel corpus EnglishWeb2020)
    
    #Completata la lettura del corpus, e individuate le frasi relative al verbo transitivo richiesto

    sents = preprocessing(frasi) #rimozione di punteggiatura e trasformazione in lower case delle frasi precedentemente selezionate

    subj_obj = []
    disambigued = []
    super_senses = []
    slot1_ss = []
    slot2_ss = []
    index = 0

    i = 0
    for sentence in tqdm(sents):
        index += 1
        #parsing
        subj_obj.append(parse_find_subj_obj(sentence, index)) #Filling slots (sub and obj) with fillers
        temp = sentence #save sentence now considered
        temp_subj = subj_obj[i][0] #save subject obtained
        temp_obj = subj_obj[i][1] #save object obtained
        sent = temp.split()
        #disambiguation
        s, o = wsd(sent, temp_subj, temp_obj) #Word Sense Disambiguation usando supersenso di Wordnet(People) o Lesk
        if s is not None and o is not None:
            so = (s, o)
            disambigued.append(so)     #Soggetti e oggetti non nulli -> memorizzati nella tupla "so"
            sup = super_sense(so[0], so[1]) #computazione dei supersensi di soggetto e oggetto trovati
            super_senses.append(sup)      #Supersensi OK
            if sup[0] is not None:
                #Supersensi dei soggetti (si elimina dalla stringa originale la funziona grammaticale "noun.person" -> "person")
                slot1_ss.append(sup[0].split('.')[1])
            else: #subj is None
                slot1_ss.append(sup[0]) #si lascia None

            if sup[1] is not None:
                #Supersensi complementi oggetti (si elimina dalla stringa originale la funziona grammaticale "noun.person" -> "person")
                slot2_ss.append(sup[1].split('.')[1])
            else: #obj is None
                slot2_ss.append(sup[1]) #si lascia None
        i += 1

    #total lenghts of subjects / objects / the list of tuples containing all the couples (subject, object)
    tot_slot1 = len(slot1_ss)
    tot_slot2 = len(slot2_ss)
    tot_ss = len(super_senses)


    #Risultati finali

    #counts elements from the list "supersenses" -> to identify the most common couples (subject, object) in the sentences
    ss_count = Counter(super_senses)
    occ = ss_count.most_common(10) #identify the 10 most common ones
    for pair, occ in occ:
        print("Semantic Type:  ", pair, round((occ/tot_ss)*100, 2), " %")
    #print("Occorrenze delle combinazioni/coppie dei filler (subj,obj) negli slot 1 e 2 \n", ss_count.most_common(10))
    #print("Totale supesensi ", tot_ss)

    #counts elements from the list "slot1_ss" -> to identify the most common fillers for the slot1 (subject) in the sentences
    slot1_count = Counter(slot1_ss)
    occ_slot1 = slot1_count.most_common(10)
    for filler1, occ in occ_slot1:
        print("Filler slot 1:  ", filler1, round((occ/tot_slot1) * 100, 2), " %")
    #Occorrenze supersensi dei soggetti\n"
    print("Totale slot 1 ", tot_slot1)

    #counts elements from the list "slot2_ss" -> to identify the most common fillers for the slot2 (object) in the sentences
    slot2_count = Counter(slot2_ss)
    occ_slot2 = slot2_count.most_common(10)
    for filler2, occ in occ_slot2:
        print("Filler slot 2:  ", filler2, round((occ/tot_slot2) * 100, 2), " %")
    #Occorrenze supersensi degli oggetti
    print("Totale slot 2 ", tot_slot2)