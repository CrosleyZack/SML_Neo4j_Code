from neo4j.v1 import GraphDatabase, basic_auth

class Graph():

    def __init__(self, connectionString = "default"):
        self.connectionString = connectionString
        self.driver = GraphDatabase.driver(connectionString, auth=basic_auth("neo4j", "password"))
        self.session = self.driver.session()
        #force all names to be unique. This is how people are identified
        self.session.run("CREATE CONSTRAINT ON (a:Author) ASSERT a.name IS UNIQUE")

    def checkNodeExists(self, author:str):
        #query database for matching author
        response = self.session.run("MATCH (a:Author) "
                                    " WHERE a.name = '" + author + "'"
                                    " RETURN a")
        #find a in response
        listresult = list(response)
        #matches = response.records()
        if len(listresult) == 0:
            return False
        else:
            return True

    def clearGraph(self):
        # query database for matching author
        response = self.session.run("MATCH (n)"
                                    " DETACH DELETE n")
        return list(response)

    def checkEdgeExists(self, author1:str, author2:str):
        #if edge is found between them, return true.
        #NOTE: "edge" is simply a variable used to reference the edge, CoAuthored is the relationship between the two authors.
        response = self.session.run("MATCH (a:Author)-[edge:CoAuthored]-(b:Author)"
                                    " WHERE a.name = '" + author1 + "' AND b.name = '" + author2 + "'"
                                    " RETURN edge")
        #TODO figure out better way to check edge exists
        listresult = list(response)
        #single_response = response.single()
        #if single_response:
        #    single_response = single_response.get("edge")
        #response_peek = response.peek()
        #summary_response = response.summary()
        #response_keys = response.keys()
        #response_allrecords = response.records()
        #edge_response = listresult.get("edge")
        if len(listresult) == 0:
            return False
        else:
            return True

    def getEdgeWeight(self, author1:str, author2:str):
        response = self.session.run("MATCH (a:Author)-[edge:CoAuthored]-(b:Author)"
                                    " WHERE a.name = '" + author1 + "' AND b.name = '" + author2 + "'"
                                    " RETURN edge.weight")
        #get weight from response
        weight = response.single()
        return weight

    def addEdge(self, author1:str, author2:str):
        #check edge exists
        edge_weight = self.getEdgeWeight(author1, author2)
        if edge_weight != None:
            #get incremented edge weight
            new_edge_weight = int(edge_weight[0]) + 1 #adds one to weight
            #set new weight property
            response = self.session.run(
                "MATCH (a:Author)-[edge:CoAuthored]-(b:Author)"
                " WHERE a.name = '" + author1 + "' AND b.name = '" + author2 + "'"
                " SET edge.weight = '" + str(new_edge_weight) + "'"
                " RETURN edge")
            #verify success and return
            to_return = response.single()
            return to_return
        else:
            #add edge with weight 1. Uses MERGE as CREATE doesn't support undirected relationships.
            response = self.session.run("MATCH (a:Author), (b:Author)"
                                        " WHERE a.name = '" + author1 + "' AND b.name = '" + author2 + "'"
                                        " MERGE (a)-[edge:CoAuthored {weight: 1}]-(b)"
                                        " RETURN edge")
            #verify success and return
            to_return = response.single()
            return to_return

    def addAuthor(self, author: str):
        #add using a merge. This means that if the node already exists, it will simply be returned.
        response = self.session.run("MERGE(a:Author {name: '" + author + "'})"
                                    " RETURN a")
        listresult = list(response)
        return listresult[0]

    def markNode(self, author:str, mark:str):
        response = self.session.run("MATCH (a:Author)"
                                    " WHERE a.name = '" + author + "'"
                                    " SET a.mark = '" + mark + "'"
                                    " RETURN a")
        toreturn = list(response)
        return toreturn

    def getMarkedNodes(self, mark:str):
        response = self.session.run("MATCH (a)"
                                    " WHERE a.mark = '" + mark + "'"
                                    " RETURN a.name"
                                    " ORDER BY a.name")
        toreturn = list(response)
        return toreturn

    def getAllAuthors(self):
        response = self.session.run("MATCH (a:Author)"
                                    " RETURN a.name"
                                    " ORDER BY a.name")
        toreturn = list(response)
        return toreturn