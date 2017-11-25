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

    def parseMAGFileUndirected(self, filepath):
        """Parses the json files from the MAG dataset"""
        with open(filepath, "r") as f:
            #track number of publications parsed
            num_publications = 0

            for line in f:

                #parse json from line
                publish_item = json.loads(line)
                #print("   Parsed json line in ", timer - time.time())

                conference = publish_item['venue']
                if not conference.lower() == "neural information processing systems":
                    continue

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

    def parseMAGFileDirected(self, filepath):
        """Parses the json files from the MAG dataset"""
        with open(filepath, "r") as f:
            # track number of publications parsed
            num_publications = 0

            for line in f:

                # parse json from line
                publish_item = json.loads(line)
                # print("   Parsed json line in ", timer - time.time())

                # get list of names from json object
                coauthors = []
                for author in publish_item['authors']:
                    coauthors.append(author['name'])

                # clean the author set to remove invalid characters
                coauthors = self.cleanAuthors(coauthors)

                # if one author is not found in graph, add them.
                for author in coauthors:
                    # we don't need to check if this node exists because add author uses merge
                    self.graph.addNode(author, "Author")
                    # print("   Added author to database in ", timer - time.time())

                # add edges: For each combination of authors, add the edge. Function automatically adds one to edge if it already exists
                for i, j in itertools.combinations(coauthors, 2):
                    if i == j:
                        continue
                    else:
                        self.graph.addEdgeWithWeight(i, j, 1, "CoAuthored")
                        self.graph.addEdgeWithWeight(j,i,1,"CoAuthored")
                        # print("   Added edge to database in ", timer - time.time())

                num_publications += 1

        return self.graph

    def parseTextFileWithWeightDirected(self, filepath):
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

    def parseTextFileDirected(self, filepath, delimeter=" ", edge_limit=100):
        """Parses file with edges defined in the form node1 node2 edge1"""
        with open(filepath, "r") as f:

            for i, line in enumerate(f):

                #Get the node1, node2, and edge weight
                node1, node2 = line.split(delimeter)
                node2 = node2.replace("\n", "")
                self.graph.addNode(node1)
                self.graph.addNode(node2)
                self.graph.addEdgeWithWeight(node1, node2, 1)
                self.graph.addEdgeWithWeight(node2, node1, 1)

                if i >= edge_limit:
                    break

        #Now, for each node, we calculate the weight
        calcLogWeights(self.graph)

        return self.graph

    def parseTextFileWithWeightUndirected(self, filepath, node_labels):
        """Parses file with edges defined in the form node1 node2 edge1"""
        node_dict = {}
        last_index = 0
        with open(filepath, "r") as f:
            #track number of publications parsed
            num_publications = 0

            for line in f:

                #Get the node1, node2, and edge weight
                node1, node2, edge_weight = line.split(' ')

                if node1 not in node_dict.keys():
                    node_dict[node1] = node_labels[last_index]
                    last_index += 1
                if node2 not in node_dict.keys():
                    node_dict[node2] = node_labels[last_index]
                    last_index += 1

                self.graph.addNode(node_dict[node1])
                self.graph.addNode(node_dict[node2])
                weight = float(edge_weight)
                self.graph.addEdgeUnlabeled(node_dict[node1], node_dict[node2])

        return self.graph

    def parseTextFileUndirected(self, filepath):
        """Parses file with edges defined in the form node1 node2 edge1"""
        node_dict = {}
        last_index = 0
        with open(filepath, "r") as f:
            #track number of publications parsed
            num_publications = 0

            for i, line in enumerate(f):

                #Get the node1, node2, and edge weight
                node1, node2 = line.split('\t')
                node2 = node2.replace("\n", "")

                self.graph.addNode(node1, "Page")
                self.graph.addNode(node2, "Page")
                self.graph.addEdge(node1, node2, "Page", "Link")

                if i > 100:
                    break

        return self.graph

    def parse2DMatrix(self, matrix, original_marked_nodes, new_marked_nodes, node_ids):
        # create our nodes
        for i in node_ids:
            self.graph.addNode(str(i))

        # create edges
        for source_node, row in zip(node_ids, matrix):
            for dest_node, edge in zip(node_ids, row):
                if edge != 0:
                    self.graph.addEdgeWithWeight(str(source_node), str(dest_node), edge, "I")

        # update nodes with class marked if marked
        for node in original_marked_nodes:
            self.graph.updateNodeClass(node, "marked", "Author")

        for node in new_marked_nodes:
            self.graph.updateNodeClass(node, "new_marked", "Author")


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

    # Preset for AMAZON DATASET
    # NOTE - Remember to delete first four header lines of file

    # Connection string for Neo4j Database
    connectionString = "bolt://10.152.114.20:7687"
    # Amazon Amazon0302.txt filepath here
    filePath = "C:\\Users\\crosl\\OneDrive\\School\\ASU\\Fall 2017\\CSE 575\\Term Project\\Dataset\\Amazon0302.txt"

    parser = Parser(connectionString, False)
    #Specify how many edges you want to read in
    graph = parser.parseTextFileDirected(filePath, delimeter="\t", edge_limit=100)
    print("Complete")


if __name__ == "__main__":
    main()