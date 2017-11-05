from neo4j.v1 import GraphDatabase, basic_auth
import random

"""Look into how to """


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

    def checkEdgeExists(self, author1:str, author2:str):
        #if edge is found between them, return true.
        #NOTE: "edge" is simply a variable used to reference the edge, CoAuthored is the relationship between the two authors.
        response = self.session.run("MATCH (a:Author)-[edge:CoAuthored]-(b:Author)"
                                    " WHERE a.name = '" + author1 + "' AND b.name = '" + author2 + "'"
                                    " RETURN edge")
        #TODO figure out better way to check edge exists
        listresult = list(response)
        if len(listresult) == 0:
            return False
        else:
            return True

    def connectedWithNLeaps(self, author1:str, author2:str, count:int, connectionType:str):
        """Finds the nodes through which node a and b can be connected
            with exactly N leaps (N edges, N-1 Nodes).of a specified
            edge type."""
        query = "MATCH (a:Author)-"
        for i in range (0, count):
            query += "[:" + connectionType + "]-"
        query += "(b:Author)"
        query += " WHERE a.name = '" + author1 + "' AND b.name = '" + author2 + "'"
        query += " RETURN "

    def getEdgeWeight(self, author1:str, author2:str):
        response = self.session.run("MATCH (a:Author)-[edge:CoAuthored]-(b:Author)"
                                    " WHERE a.name = '" + author1 + "' AND b.name = '" + author2 + "'"
                                    " RETURN edge.weight")
        #get weight from response
        weight = response.single()
        toreturn = None
        if weight != None:
            toreturn = weight[0]
        return toreturn

    def addEdgeWithWeight(self, author1:str, author2:str, weight:int):
        response = self.session.run(
            "MATCH (a:Author), (b:Author)"
            " WHERE a.name = '" + author1 + "' AND b.name = '" + author2 + "'"
            " MERGE (a)-[edge:CoAuthored {weight:" + weight + "}]-(b)"
            " RETURN edge")
        # verify success and return
        to_return = response.single()
        return to_return

    def addEdge(self, author1:str, author2:str):
        #check edge exists
        edge_weight = self.getEdgeWeight(author1, author2)
        if edge_weight != None:
            #get incremented edge weight
            new_edge_weight = int(edge_weight) + 1 #adds one to weight
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
                                        " MERGE (a)-[edge:CoAuthored {weight:1}]-(b)"
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

    def markNodes(self, nodes:list, mark:str):
        #mark each node with the passed in mark
        for node in nodes:
            self.markNode(node, mark)

    def markNode(self, author:str, mark:str):
        response = self.session.run("MATCH (a:Author)"
                                    " WHERE a.name = '" + author + "'"
                                    " SET a.mark = '" + mark + "'"
                                    " RETURN a")
        toreturn = list(response)
        return toreturn

    def addPartitionLabelToNodes(self, authors:list, partitionId:str):
        toreturn = list()
        for author in authors:
            response = self.addPartitionLabelToNode(author, partitionId)
            toreturn += response
        return toreturn

    def addPartitionLabelToNode(self, author:str, partitionId:str):
        response = self.session.run("MATCH (a:Author)"
                                    " WHERE a.name = '" + author + "'"
                                    " SET a.partition = '" + partitionId + "'"
                                    " RETURN a")
        toreturn = list(response)
        return toreturn

    def getNodesInPartition(self, partitionId:str):
        response = self.session.run("MATCH (a:Author)"
                                    " WHERE a.partition = '" + partitionId + "'"
                                    " RETURN a.name")
        toreturn = list(response)
        return toreturn

    def getMarkedNodes(self, mark:str):
        response = self.session.run("MATCH (a)"
                                    " WHERE a.mark = '" + mark + "'"
                                    " RETURN a.name"
                                    " ORDER BY a.name")
        toreturn = list(response)
        toreturn = [x[0] for x in toreturn]
        return toreturn

    def getAllAuthors(self):
        response = self.session.run("MATCH (a:Author)"
                                    " RETURN a.name"
                                    " ORDER BY a.name")
        toreturn = list(response)
        toreturn = [x[0] for x in toreturn]
        return toreturn

    def getNeighboringNodes(self, author:str):
        response = self.session.run("MATCH (a:Author)-[c:CoAuthored]-(b:Author)"
                                    " WHERE a.name = '" + author + "'"
                                    " RETURN b.name"
                                    " ORDER BY c.weight")
        toreturn = list(response)
        toreturn = [x[0] for x in toreturn]
        return toreturn

    def getNumberOfNeighbors(self, author:str):
        response = self.session.run("MATCH (a:Author)-[:CoAuthored]-(b:Author)"
                                    " WHERE a.name = '" + author + "'"
                                    " RETURN count(b)")
        toreturn = list(response)
        toreturn = toreturn[0][0]
        return toreturn

    def getEdgesOffNodes(self, authors:list):
        """takes in a list of authors, returns a dictionary of author to the set of edges
        and their targets from that node."""
        toreturn = {}
        for author in authors:
            #create dictionary mapping for author
            toreturn[author] = dict()

            response = self.session.run("MATCH (a:Author)-[e:CoAuthored]-(b:Author)"
                                    " WHERE a.name = '" + author + "'"
                                    " RETURN e.weight, b.name")
            templist = list(response)
            for return_item in templist:
                edge_weight = return_item[0]
                neighbor = return_item[1]

                #append to the return for this author the pair (edge_weight, neighbor)
                toreturn[author][neighbor] = float(edge_weight)

        return toreturn

    def getEdgesOffAllNodes(self):
        """takes in a list of authors, returns a dictionary of author to the set of edges
        and their targets from that node."""
        return self.getEdgesOffNodes(self.getAllAuthors())

    def clearGraph(self):
        # query database for matching author
        response = self.session.run("MATCH (n)"
                                    " DETACH DELETE n")
        return list(response)


    def getRandomNodes(self, count:int):
        author_list = self.getAllAuthors()
        # by default we return None to indicate that the command couldn't be executed
        toreturn = None
        # if the list of authors is sufficiently long, get count random items
        if len(author_list) >= count:
            toreturn = random.sample(author_list, count)
        return toreturn