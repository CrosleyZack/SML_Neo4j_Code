import json
import dbWriter
import itertools
import time
import random

class Parser():

    def __init__(self, connectionString = "default"):
        self.graph = dbWriter.Graph(connectionString)

    def parseFile(self, filepath):
        with open(filepath, "r") as f:
            #track number of publications parsed
            num_publications = 0

            for line in f:

                #parse json from line
                timer = time.time()
                publish_item = json.loads(line)
                print("   Parsed json line in ", timer - time.time())

                #get list of names from json object
                coauthors = []
                for author in publish_item['authors']:
                    coauthors.append(author['name'])

                coauthors = self.cleanAuthors(coauthors)

                #if one author is not found in graph, add them.
                for author in coauthors:

                    #we don't need to check if this node exists because add author uses merge
                    #if self.graph.checkNodeExists(author) == False:

                    timer = time.time()
                    self.graph.addAuthor(author)
                    print("   Added author to database in ", timer - time.time())

                #add edges: For each combination of authors, add the edge. Function automatically adds one to edge if it already exists
                for i, j in itertools.combinations(coauthors, 2):
                    if i == j:
                        continue
                    else:
                        timer = time.time()
                        self.graph.addEdge(i,j)
                        print("   Added edge to database in ", timer - time.time())

                num_publications += 1
                print("Completed Line ", str(num_publications))


    def viewFile(filepath):
        with open(filepath) as f:
            for line in f:
                print(line)

    def resetGraph(self):
        self.graph.clearGraph()

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

    def getRandomNodes(self, count:int):
        author_list = self.graph.getAllAuthors()
        author_pairs = random.sample(author_list, count)
        toreturn = [x[0] for x in author_pairs]

        return toreturn

    def markNodes(self, nodes, mark):
        for node in nodes:
            self.graph.markNode(node, mark)

    def getMarkedNodes(self, mark:str):
        return self.graph.getMarkedNodes(mark)


def main():
    connectionString = "bolt://localhost:7687"
    parser = Parser(connectionString)

    jsonFile = "C:\\Users\\crosl\\OneDrive\\School\\ASU\\Fall 2017\\CSE 575\\Term Project\\Dataset\\mag_papers_166.txt"
    parser.parseFile(jsonFile)

    #Change this to specify a mark to use. This means there could exist multiple marks at once
    mark = "marked"

    #Use this to specify the nodes to mark by author name manually
    nodesToMark = ["Conner Gh", ""]
    #use this to generate random nodes to mark
    numberOfNodesToMark = 4
    nodes = parser.getRandomNodes(numberOfNodesToMark)

    #mark nodes
    parser.markNodes(nodes, mark)

    #retrive marked nodes (TEST)
    nodes = parser.getMarkedNodes(mark)

    #clear graph
    parser.resetGraph()


if __name__ == "__main__":
    main()