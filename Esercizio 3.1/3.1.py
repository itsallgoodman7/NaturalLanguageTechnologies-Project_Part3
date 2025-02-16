from neo4j import GraphDatabase
from py2neo import Graph
import pandas as pd
import os
import tqdm

path = os.path.dirname(__file__)

#Start session
def initialize():
    driver=GraphDatabase.driver(uri='bolt://localhost:7687',auth = ("neo4j", "pippo"))

    session = driver.session()

    delete_all_nodes_and_relationships(session)

    return session

#Cleaning the Graph
def delete_all_nodes_and_relationships(session):

    delete_rel = '''MATCH (n)-[r]->()
    DELETE r'''

    session.run(delete_rel)

    delete_nodes = '''MATCH (n) DELETE n'''

    session.run(delete_nodes)

#Database Population (node labels and relations)
def dbpopulation(session):

    df = pd.read_csv(path + '/euro2020.csv') # loading the dataset

    # creation of the nodes, taking all the columuns of interest from the dataset
    Country = df["Country"].unique()

    Player = df["Player"].unique()

    Goals = df["Goals"].unique()

    MatchPlayed = df["Matchplayed"].unique()

    Position = df["Position"].unique()

    DistanceCovered = df["Distancecovered"].unique()

    #creation of the first relationship: A = Player, B = Country -> A plays_for B)
    Country_of = '''MERGE(A:Player{Player:$Player})
        MERGE(B:Country{Country:$Country})
        MERGE (A)-[:plays_for]->(B)
        '''
    #creation of the second relationship: A = Player, B = Goals, C = MatchPlayed -> A scored_goals_number B in_matches_number C)
    GoalsPerMatch = '''MERGE(A:Player{Player:$Player})
        MERGE(B:Goals{Goals:$Goals})
        MERGE(C:MatchPlayed{MatchPlayed:$Matchplayed})
        MERGE (C)<-[:in_matches_number]-(A)-[:scored_goals_number]->(B)
        '''
    #creation of the third relationship: A = Player, B = DistanceCovered, C = Position -> A covered_tot_km B playing_as C)
    KmCovered_as_Role = '''MERGE(A:Player{Player:$Player})
        MERGE(B:DistanceCovered{DistanceCovered:$Distancecovered})
        MERGE(C:Position{Position:$Position})
        MERGE (C)<-[:playing_as]-(A)-[:covered_tot_km]->(B)
        '''

    for p in Player: # "central" node to be attached to additional peripheral nodes
        row = df[df.Player == p]   #takes a row (from the data)
        
        #filling central node (Player) and peripheral nodes (Goals, Country, Goals, ecc.) with data
        #storing nodes data (retrieved from the dataset) into lists
        for index,Player in enumerate(row['Player']):
            Country = list(row['Country'])[index]
            Goals = list(row['Goals'])[index]
            MatchPlayed = list(row['Matchplayed'])[index]
            Position = list(row['Position'])[index]
            DistanceCovered = list(row['Distancecovered'])[index]
        
        #storing all informations relative to all the nodes created
        parsed_dict ={'Country':Country, 'Player':Player, 'Goals':Goals, 'Matchplayed':MatchPlayed, 'Position':Position, 'Distancecovered':DistanceCovered}
            
        # run first relation with attached informations (parsed_dict)
        session.run(Country_of,parsed_dict)
        # run second relation with attached informations (parsed_dict)
        session.run(GoalsPerMatch, parsed_dict)
        # run third relation with attached informations (parsed_dict)
        session.run(KmCovered_as_Role, parsed_dict)

def queries():
    graph = Graph('bolt://localhost:7687', auth=("neo4j", "pippo"))

    #Data Visualization (queries on the data loaded)
    print ("\n")

    #(visualize on Neo4jBrowser) # "MATCH p="" and "RETURN P" in order to visualize the entire graph resulting from the query
    # MATCH p=()<-[playing_as]-()-[r:plays_for]->() RETURN p LIMIT 25
    # MATCH p=()<-[playing_as]-()-[r:plays_for]->({Country:'Italy'}) RETURN p LIMIT 25

    # first query to search all the players who plays for Italy
    query1 = graph.run("MATCH (p)-[r:plays_for]->(c{Country:'Italy'}) RETURN p,c LIMIT 25").data()
    print("< Italy Team - Top Players of Euro2020: >" + "\n")
    for elem in query1:
        print(f"Player Full Name - {elem['p']['Player']} -- {elem['c']['Country']}")
        #print(elem)

    print ("\n" + "---------------------" + "\n")

    # second query to search all the players who plays for Italy and on which position
    query2 = graph.run("MATCH (position)<-[r1:playing_as]-(player)-[r:plays_for]->({Country:'Italy'}) RETURN player,position LIMIT 26").data()
    print("< Italy Team - Top Players and their role in the squad: >" + "\n")
    for elem in query2:
        print(f"Player: {elem['player']['Player']} plays in role: {elem['position']['Position']} for Italy")

    print("\n" + "---------------------" + "\n")

    #third query to search the EURO2020 top scorer players
    query3 = graph.run("MATCH (n)-[r:scored_goals_number]->(g{Goals:5}) RETURN n,g").data()
    print("< Euro2020 - Top Scorers: >" + "\n")
    for elem in query3:
        print(elem['n']['Player'] + ' has scored a total of ' + str(elem['g']['Goals']) + " goals")

    print ("\n" + "---------------------" + "\n")

    #bonus query to show the 10 players who scored the most goals in EURO2020, viewing also how many matches they've played
    querybonus = graph.run("MATCH (matches)<-[r1:in_matches_number]-(player)-[r:scored_goals_number]->(goals) RETURN player,goals,matches ORDER BY goals.Goals DESC LIMIT 10").data()
    print("< Euro2020 - Players ranked by their goals scored: >" + "\n")
    for elem in querybonus:
        print(f"Player: {elem['player']['Player']} has scored tot number goals: {elem['goals']['Goals']} in tot number matches played: {elem['matches']['MatchPlayed']}")

    print ("\n" + "---------------------" + "\n")

    # fourth query to search the 10 players with most total kilometers covered in the field
    query4 = graph.run("MATCH (p)-[r:covered_tot_km]->(d) RETURN p,d ORDER BY d.DistanceCovered DESC LIMIT 10").data()
    print("< Euro2020 - Players ranked by total kilometers covered: >" + "\n")
    for elem in query4:
        if float(elem['d']['DistanceCovered']) > 50.0:
            print(f"{elem['p']['Player']} covered a tot distance of {elem['d']['DistanceCovered']}")

    print("\n" + "---------------------" + "\n")

#start database connection (session) on neo4j
driver=GraphDatabase.driver(uri='bolt://localhost:7687',auth = ("neo4j", "pippo"))
session = driver.session()

#delete previous nodes and relationships
delete_all_nodes_and_relationships(session)

#execute database population
dbpopulation(session)

#execute queries
print("\n\nEsercizio 3.1 - Neo4j data visualization and data queries:\n")
queries()