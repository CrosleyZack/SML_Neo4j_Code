import json
import dbWriter
import itertools
import math

class Parser():

    def __init__(self, connectionString = "default", directed=False):
        if not directed:
            self.graph = dbWriter.Graph(connectionString)
        else:
            self.graph = dbWriter.DirectedGraph(connectionString)

    def parseMAGFile(self, filepath):
        """Parses the json files from the MAG dataset"""
        with open(filepath, "r") as f:
            #track number of publications parsed
            num_publications = 0

            for line in f:

                #parse json from line
                publish_item = json.loads(line)
                #print("   Parsed json line in ", timer - time.time())

                #get list of names from json object
                coauthors = []
                for author in publish_item['authors']:
                    coauthors.append(author['name'])

                #clean the author set to remove invalid characters
                coauthors = self.cleanAuthors(coauthors)

                #if one author is not found in graph, add them.
                for author in coauthors:
                    #we don't need to check if this node exists because add author uses merge
                    self.graph.addNode(author)
                    #print("   Added author to database in ", timer - time.time())

                #add edges: For each combination of authors, add the edge. Function automatically adds one to edge if it already exists
                for i, j in itertools.combinations(coauthors, 2):
                    if i == j:
                        continue
                    else:
                        self.graph.addEdge(i,j)
                        #print("   Added edge to database in ", timer - time.time())

                num_publications += 1
                #print("Completed Line ", str(num_publications))
                if num_publications == 100:
                    break

        return self.graph

    def parseTextFileDirected(self, filepath):
        """Parses file with edges defined in the form node1 node2 edge1"""
        with open(filepath, "r") as f:
            #track number of publications parsed
            num_publications = 0

            for line in f:

                #Get the node1, node2, and edge weight
                node1, node2, edge_weight = line.split(' ')
                self.graph.addNode(node1)
                self.graph.addNode(node2)
                weight = float(edge_weight)
                self.graph.addEdgeWithWeight(node1, node2, edge_weight)
                self.graph.addEdgeWithWeight(node2, node1, edge_weight)

        #Now, for each node, we calculate the weight
        calcLogWeights(self.graph)

        return self.graph

    @staticmethod
    def viewFile(filepath):
        with open(filepath) as f:
            for line in f:
                print(line)

    @staticmethod
    def cleanAuthors(authors):
        toreturn = []
        #for each author
        for author in authors:
            #replace each invalid character in author
            cleaned_author = author
            for ch in ["'"]:
                cleaned_author = cleaned_author.replace(ch, "")
            #add cleaned author to return list
            toreturn.append(cleaned_author)
        return toreturn

"""Function for seeing how many venues existed in the file. Just for 
testing purposes."""
def getNumberOfVenues(filepath: str):
    with open(filepath, "r") as f:
        # track number of publications parsed
        num_venues = 0
        unknown_venue = 0
        venueList = []

        for line in f:
            publish_item = json.loads(line)

            try:
                this_venue = publish_item['venue']

                if not this_venue in venueList:
                    num_venues += 1
                    venueList.append(this_venue)

                if num_venues % 1000 == 0:
                    print("Reached " + str(num_venues) + " venues")
            except:
                unknown_venue += 1

                if unknown_venue % 1000 == 0:
                    print("Reached " + str(num_venues) + " unknown venues")

        #print("Total number of Venues: " + str(num_venues))
        #print("Total number of unknown Venues: " + str(unknown_venue))

"""Tests the marking functionality. Just for testing purposes."""
def test_mark(graph):
    # Change this to specify a mark to use. This means there could exist multiple marks at once
    mark = "marked"

    # A. Use this to specify the nodes to mark by author name manually
    # nodesToMark = ["Conner Gh", ""]
    # B. use this to generate random nodes to mark
    numberOfNodesToMark = 10
    nodes = graph.getRandomNodes(numberOfNodesToMark)

    # If marked nodes couldn't be generated, return
    if nodes == None:
        return

    # mark nodes
    graph.markNodes(nodes, mark)

    # retrieve marked nodes (TEST)
    nodes = graph.getMarkedNodes(mark)

    # get all edges off marked nodes
    test = graph.getEdgesOffNodes(nodes)

    print[test]

def calcLogWeights(graph):
    for node in graph.getAllNodes():
        neighbors = graph.getNeighboringNodes(node)
        out_edges = len(neighbors)
        weight = math.log(out_edges, 2)
        for neighbor in neighbors:
            graph.setEdgeWeight(node, neighbor, weight)

def main():
    # Connection string for Neo4j Database
    connectionString = "bolt://127.0.0.1:7687"

    # UNCOMMENT THIS SECTION TO READ IN FROM FILE
    parser = Parser(connectionString, True)
    file = "gridtest.txt"
    graph = parser.parseTextFileDirected(file)

    # UNCOMMENT THIS SECTION TO ACCESS EXISTING DATABASE, NO READ IN NECESSARY
    # graph = dbWriter.Graph(connectionString)

if __name__ == "__main__":
    main()