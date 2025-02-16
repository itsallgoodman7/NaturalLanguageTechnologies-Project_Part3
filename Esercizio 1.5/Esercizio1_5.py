import utils as ut
import os

path_ = os.path.dirname(__file__)
open(path_ + "/output/allFoundConcepts.txt", "w").close()

#getting the definitions
res = ut.loadCsv(path_ + "/input/defs.csv")

#processing the definitions -> obtaining the most common words used in the definitions
#(all the words used with their frequency, sorted by descending order)
definitions_1 = ut.getCommonWords(res[0])
#print(definitions_1)
definitions_2 = ut.getCommonWords(res[1])
definitions_3 = ut.getCommonWords(res[2])
definitions_4 = ut.getCommonWords(res[3])

#content to form (from the definitions obtain the correct WordNet synset intended for the real concept)
concept1 = ut.getConcepts(definitions_1[:3], definitions_1) #params: 3 most common words, complete list of definitions (=context)
concept2 = ut.getConcepts(definitions_2[:3], definitions_2)
concept3 = ut.getConcepts(definitions_3[:3], definitions_3)
concept4 = ut.getConcepts(definitions_4[:3], definitions_4)

#create a table and writing results
table_result = ut.getTableResult(concept1, concept2, concept3, concept4)
ut.writeTable(table_result, path_ + "/output/bestConcepts.txt") #storing results of the 10 best synsets found
ut.writeResults(concept1, concept2, concept3, concept4)