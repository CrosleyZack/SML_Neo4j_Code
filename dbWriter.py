from neo4j.v1 import GraphDatabase, basic_auth
import random

class Graph():

    def __init__(self, connectionString = "default"):
        self.connectionString = connectionString
        self.driver = GraphDatabase.driver(connectionString, auth=basic_auth("neo4j", "password"))
        self.session = self.driver.session()

        #create the type of nodes and their relationships
        self.node_relationship = "CoAuthored"
        self.node_class = "Author"
        #force all names to be unique. This is how people are identified
        self.session.run("CREATE CONSTRAINT ON (a:" + self.node_class + ") ASSERT a.name IS UNIQUE")

    def checkNodeExists(self, node:str):
        #query database for matching author
        response = self.session.run("MATCH (a:" + self.node_class + ") "
                                    " WHERE a.name = '" + node + "'"
                                    " RETURN a")
        #find a in response
        listresult = list(response)
        #matches = response.records()
        if len(listresult) == 0:
            return False
        else:
            return True

    def checkEdgeExists(self, node1:str, node2:str):
        #if edge is found between them, return true.
        #NOTE: "edge" is simply a variable used to reference the edge, CoAuthored is the relationship between the two authors.
        response = self.session.run("MATCH (a:" + self.node_class + ")-[edge:" + self.node_relationship + "]-(b:Author)"
                                    " WHERE a.name = '" + node1 + "' AND b.name = '" + node2 + "'"
                                    " RETURN edge")
        #TODO figure out better way to check edge exists
        listresult = list(response)
        if len(listresult) == 0:
            return False
        else:
            return True

    def connectedWithNLeaps(self, node1:str, node2:str, count:int, connectionType:str):
        """Finds the nodes through which node a and b can be connected
            with exactly N leaps (N edges, N-1 Nodes).of a specified
            edge type."""
        query = "MATCH (a:" + self.node_class + ")-"
        for i in range (0, count):
            query += "[:" + connectionType + "]-"
        query += "(b:" + self.node_class + ")"
        query += " WHERE a.name = '" + node1 + "' AND b.name = '" + node2 + "'"
        query += " RETURN "

    def getEdgeWeight(self, node1:str, node2:str):
        response = self.session.run("MATCH (a:" + self.node_class + ")-[edge:" + self.node_relationship + "]-(b:" + self.node_class +")"
                                    " WHERE a.name = '" + node1 + "' AND b.name = '" + node2 + "'"
                                    " RETURN edge.weight")
        #get weight from response
        weight = response.single()
        toreturn = None
        if weight != None:
            toreturn = weight[0]
        return toreturn

    def addEdgeWithWeight(self, node1:str, node2:str, weight:float):
        """Creates an edge """
        response = self.session.run(
            "MATCH (a:" + self.node_class + "), (b:" + self.node_class + ")"
            " WHERE a.name = '" + node1 + "' AND b.name = '" + node2 + "'"
            " MERGE (a)-[edge:" + self.node_relationship + " {weight:" + weight + "}]-(b)"
            " RETURN edge")
        # verify success and return
        to_return = response.single()
        return to_return

    def addEdge(self, node1:str, node2:str):
        """Creates an undirected edge between node1 and node2. Edge weight is incremented by one from previous edge weight
            or is initialized to one if no prior edge existed."""
        #check edge exists
        edge_weight = self.getEdgeWeight(node1, node2)
        if edge_weight != None:
            #get incremented edge weight
            new_edge_weight = int(edge_weight) + 1 #adds one to weight
            #set new weight property
            response = self.session.run(
                "MATCH (a:" + self.node_class + ")-[edge:" + self.node_relationship + "]-(b:" + self.node_class +")"
                " WHERE a.name = '" + node1 + "' AND b.name = '" + node2 + "'"
                " SET edge.weight = '" + str(new_edge_weight) + "'"
                " RETURN edge")
            #verify success and return
            to_return = response.single()
            return to_return
        else:
            #add edge with weight 1. Uses MERGE as CREATE doesn't support undirected relationships.
            response = self.session.run("MATCH (a:" + self.node_class + "), (b:" + self.node_class + ")"
                                        " WHERE a.name = '" + node1 + "' AND b.name = '" + node2 + "'"
                                        " MERGE (a)-[edge:" + self.node_relationship + " {weight:1}]-(b)"
                                        " RETURN edge")
            #verify success and return
            to_return = response.single()
            return to_return

    """REPLACES ADD AUTHOR"""
    def addNode(self, node: str):
        #add using a merge. This means that if the node already exists, it will simply be returned.
        response = self.session.run("MERGE(a:" + self.node_class + " {name: '" + node + "'})"
                                    " RETURN a")
        listresult = list(response)
        return listresult[0]

    def addAuthor(self, node: str):
        #add using a merge. This means that if the node already exists, it will simply be returned.
        response = self.session.run("MERGE(a:" + self.node_class + " {name: '" + node + "'})"
                                    " RETURN a")
        listresult = list(response)
        return listresult[0]

    def markNodes(self, nodes:list, mark:str):
        #mark each node with the passed in mark
        for node in nodes:
            self.markNode(node, mark)

    def markNode(self, node:str, mark:str):
        response = self.session.run("MATCH (a:" + self.node_class + ")"
                                    " WHERE a.name = '" + node + "'"
                                    " SET a.mark = '" + mark + "'"
                                    " RETURN a")
        toreturn = list(response)
        return toreturn

    def addPartitionLabelToNodes(self, nodes:list, partitionId:str):
        toreturn = list()
        for node in nodes:
            response = self.addPartitionLabelToNode(node, partitionId)
            toreturn += response
        return toreturn

    def addPartitionLabelToNode(self, node:str, partitionId:str):
        response = self.session.run("MATCH (a:" + self.node_class + ")"
                                    " WHERE a.name = '" + node + "'"
                                    " SET a.partition = '" + partitionId + "'"
                                    " RETURN a")
        toreturn = list(response)
        return toreturn

    def getNodesInPartition(self, partitionId:str):
        response = self.session.run("MATCH (a)"
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

    "Replaces getAllAuthors"
    def getAllNodes(self):
        response = self.session.run("MATCH (a:" + self.node_class + ")"
                                    " RETURN a.name"
                                    " ORDER BY a.name")
        toreturn = list(response)
        toreturn = [x[0] for x in toreturn]
        return toreturn

    def getAllAuthors(self):
        response = self.session.run("MATCH (a:" + self.node_class + ")"
                                    " RETURN a.name"
                                    " ORDER BY a.name")
        toreturn = list(response)
        toreturn = [x[0] for x in toreturn]
        return toreturn

    def getNeighboringNodes(self, node:str):
        response = self.session.run("MATCH (a:" + self.node_class + ")-[c:" + self.node_relationship + "]-(b:" + self.node_class + ")"
                                    " WHERE a.name = '" + node + "'"
                                    " RETURN b.name"
                                    " ORDER BY c.weight")
        toreturn = list(response)
        toreturn = [x[0] for x in toreturn]
        return toreturn

    def getNumberOfNeighbors(self, node:str):
        response = self.session.run("MATCH (a:" + self.node_class + ")-[:" + self.node_relationship + "]-(b:" + self.node_class + ")"
                                    " WHERE a.name = '" + node + "'"
                                    " RETURN count(b)")
        toreturn = list(response)
        toreturn = toreturn[0][0]
        return toreturn

    def getEdgesOffNodes(self, nodes:list):
        """takes in a list of authors, returns a dictionary of author to the set of edges
        and their targets from that node."""
        toreturn = {}
        for node in nodes:
            #create dictionary mapping for author
            toreturn[node] = dict()

            response = self.session.run("MATCH (a:" + self.node_class + ")-[e:" + self.node_relationship + "]-(b:" + self.node_class + ")"
                                    " WHERE a.name = '" + node + "'"
                                    " RETURN e.weight, b.name")
            templist = list(response)
            for return_item in templist:
                edge_weight = return_item[0]
                neighbor = return_item[1]

                #append to the return for this author the pair (edge_weight, neighbor)
                toreturn[node][neighbor] = float(edge_weight)

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
        node_list = self.getAllAuthors()
        # by default we return None to indicate that the command couldn't be executed
        toreturn = None
        # if the list of authors is sufficiently long, get count random items
        if len(node_list) >= count:
            toreturn = random.sample(node_list, count)
        return toreturn




class DirectedGraph():

    def __init__(self, connectionString="default"):
        self.connectionString = connectionString
        self.driver = GraphDatabase.driver(connectionString, auth=basic_auth("neo4j", "password"))
        self.session = self.driver.session()

    # ------------------ Node Management Code ---------------------

    def checkNodeExists(self, node: str, node_type = "default"):
        """ Returns boolean indicating if that node exists in the database """
        response = self.session.run("MATCH (a:" + node_type + ") "
                                    " WHERE a.name = '" + node + "'"
                                    " RETURN a")
        # find a in response
        listresult = list(response)
        if len(listresult) == 0:
            return False
        else:
            return True

    def addNode(self, node: str, node_type="default"):
        """ Returns Neo4j response object if successful. If not an empty list,
        it is safe to assume this executed successfully """
        #add using a merge. This means that if the node already exists, it will simply be returned.
        response = self.session.run("MERGE(a:" + node_type + " {name: '" + node + "'})"
                                    " RETURN a")
        listresult = list(response)
        return listresult[0]

    def getAllNodes(self):
        """ Returns a list of strings corresponding to each node in the graph"""
        response = self.session.run("MATCH (a)"
                                    " RETURN a.name"
                                    " ORDER BY a.name")
        toreturn = list(response)
        toreturn = [x[0] for x in toreturn]
        return toreturn

    # ----------------- Node-Edge Combo Functions -----------------------

    def getNeighboringNodes(self, node:str, edge_type="default"):
        """ Returns list of strings corresponding to the nodes neighboring the provided
            node in the graph."""
        response = self.session.run("MATCH (a)-[c:" + edge_type + "]->(b)"
                                    " WHERE a.name = '" + node + "'"
                                    " RETURN b.name"
                                    " ORDER BY c.weight")
        toreturn = list(response)
        toreturn = [x[0] for x in toreturn]
        return toreturn

    def getEdgesOffNodes(self, nodes:list, edge_type="default"):
        """Returns a two layer dictionary that:
             1. passed in a graph node returns a dictionary where the keys are the nodes neighbors]
             2. passing in a nodes neighbor returns the weight of that edge

             For example, suppose we have a two node graph with nodes 1 and 2 with edge of weight 1 from 1 to 2.
             This function will return a dictionary d such that d[1] = {2: 1}"""
        toreturn = {}
        for node in nodes:
            #create dictionary mapping for author
            toreturn[node] = dict()

            response = self.session.run("MATCH (a:)-[e:" + edge_type + "]-(b)"
                                        " WHERE a.name = '" + node + "'"
                                        " RETURN e.weight, b.name")
            templist = list(response)
            for return_item in templist:
                edge_weight = return_item[0]
                neighbor = return_item[1]

                #append to the return for this author the pair (edge_weight, neighbor)
                toreturn[node][neighbor] = float(edge_weight)

        return toreturn

    def getEdgesOffAllNodes(self):
        """takes in a list of authors, returns a dictionary of author to the set of edges
        and their targets from that node."""
        return self.getEdgesOffNodes(self.getAllAuthors())

    # ------------------ Edge Management Code ---------------------

    def checkEdgeExists(self, source_node:str, target_node:str, edge_type = "default"):
        """returns a boolean indicating if an edge between those two nodes was found"""
        #if edge is found between them, return true.
        #NOTE: "edge" is simply a variable used to reference the edge, CoAuthored is the relationship between the two authors.
        response = self.session.run("MATCH (a)-[edge:" + edge_type + "]->(b)"
                                    " WHERE a.name = '" + source_node + "' AND b.name = '" + target_node + "'"
                                    " RETURN edge")
        listresult = list(response)
        if len(listresult) == 0:
            return False
        else:
            return True

    def getEdgeWeight(self, source_node:str, target_node:str, edge_type="default"):
        """Returns a float corresponding tohe weight of the edge from the source to target node"""
        response = self.session.run("MATCH (a)-[edge:" + edge_type + "]->(b)"
                                    " WHERE a.name = '" + source_node + "' AND b.name = '" + target_node + "'"
                                    " RETURN edge.weight")
        #get weight from response
        weight = response.single()
        toreturn = None
        if weight != None:
            toreturn = weight[0]
        return toreturn

    def getNumberOfNeighbors(self, node:str, edge_type="default"):
        """Returns an integer indicating the number of nodes adjacent to the provided node"""
        response = self.session.run("MATCH (a)-[:" + edge_type + "]->(b)"
                                    " WHERE a.name = '" + node + "'"
                                    " RETURN count(b)")
        toreturn = list(response)
        toreturn = toreturn[0][0]
        return toreturn

    def addEdgeWithWeight(self, source_node:str, dest_node:str, weight:float, edge_type="default"):
        """Returns a neo4j response object. Safe to assume if NOT null or empty that the operation was successful"""
        response = self.session.run(
            "MATCH (a), (b)"
            " WHERE a.name = '" + source_node + "' AND b.name = '" + dest_node + "'"
            " MERGE (a)-[edge:" + edge_type + " {weight:" + weight + "}]->(b)"
            " RETURN edge")
        # verify success and return
        to_return = response.single()
        return to_return

    def setEdgeWeight(self, source_node:str, dest_node:str, weight:float, edge_type="default"):
        """Returns a neo4j response object. Safe to assume if NOT null or empty that the operation was successful"""
        response = self.session.run("MATCH (a)-[edge:" + edge_type + "]-(b)"
                                    " WHERE a.name = '" + source_node + "' AND b.name = '" + dest_node + "'"
                                    " SET edge.weight = " + str(weight) +
                                    " RETURN edge")
        return response.single()

    # ------------------ Mark Label Code ---------------------

    def markNodes(self, nodes:list, mark:str):
        """Returns a list of Neo4j response objects. Safe to assume successful if length of response is equal to the length
        of the nodes list passed in"""
        #mark each node with the passed in mark
        toreturn = []
        for node in nodes:
            response = self.markNode(node, mark)
            toreturn.append(response)
        return toreturn

    def markNode(self, node:str, mark:str):
        """returns a neo4j response object if successful. Safe to assume success if NOT null or empty"""
        response = self.session.run("MATCH (a)"
                                    " WHERE a.name = '" + node + "'"
                                    " SET a.mark = '" + mark + "'"
                                    " RETURN a")
        toreturn = list(response)
        return toreturn

    def getMarkedNodes(self, mark:str):
        """Returns list of strings corresponding to the nodes which have that mark"""
        response = self.session.run("MATCH (a)"
                                    " WHERE a.mark = '" + mark + "'"
                                    " RETURN a.name"
                                    " ORDER BY a.name")
        toreturn = list(response)
        toreturn = [x[0] for x in toreturn]
        return toreturn

    # ------------------ Partition Label Code ---------------------

    def addPartitionLabelToNodes(self, nodes:list, partitionId:str):
        """Returns list of Neo4j response objects if successful. Safe to assume success if length of result is equal
        to the number of nodes passed in"""
        toreturn = list()
        for node in nodes:
            response = self.addPartitionLabelToNode(node, partitionId)
            toreturn += response
        return toreturn

    def addPartitionLabelToNode(self, node:str, partitionId:str):
        """Returns neo4j response object if successful. Safe to assume success if result is NOT null or empty"""
        response = self.session.run("MATCH (a)"
                                    " WHERE a.name = '" + node + "'"
                                    " SET a.partition = '" + partitionId + "'"
                                    " RETURN a")
        toreturn = list(response)
        return toreturn

    def getNodesInPartition(self, partitionId:str):
        """Returns list of strings corresponding to the nodes in that partition"""
        response = self.session.run("MATCH (a)"
                                    " WHERE a.partition = '" + partitionId + "'"
                                    " RETURN a.name")
        toreturn = list(response)
        return toreturn

    # ---------------- Other Utility Functions --------------------
    def clearGraph(self):
        """returns neo4j object if successful. Safe to assume success if not null or empty"""
        # query database for matching author
        response = self.session.run("MATCH (n)"
                                    " DETACH DELETE n")
        return list(response)

    def getRandomNodes(self, count:int):
        """Returns list of strings corresponding to nodes in the graph"""
        node_list = self.getAllAuthors()
        # by default we return None to indicate that the command couldn't be executed
        toreturn = None
        # if the list of authors is sufficiently long, get count random items
        if len(node_list) >= count:
            toreturn = random.sample(node_list, count)
        return toreturn