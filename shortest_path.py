import dbWriter
import math
import FindMST
from pprint import pprint
import numpy as np

#############################################
class MarkedPath:

    def __init__(self,source,cost,path):
        self.source = source
        self.cost = cost
        self.path = path

#############################################

def addMarkedPath(markedPaths, id, source, cost, path):
    markedPathObj = MarkedPath(source, cost, path)
    if markedPaths.get(id):
        value = markedPaths.get(id)
        value.append(markedPathObj)
        markedPaths[id] = value
    else:
        value = []
        value.append(markedPathObj)
        markedPaths[id] = value
        #print(id, markedPathObj.source, markedPathObj.cost, markedPathObj.path)

#################################################################################

def findMST(markedPaths, markedSet, graphDB, maxLength):
    minimum_paths = []
    k = markedSet.__len__()
    total_cost = 0
    SP = [[0 for j in range(k+1)] for i in range(k+1)]
    N = graphDB.getAllNodes().__len__()
    for i in range(0,k):
        SP[i][k] = math.log(N,2)
    for i in range(0,k):
        if(markedPaths.get(markedSet[i])):
            paths = markedPaths.get(markedSet[i])
            paths = sorted(paths, key=lambda p: p.cost)
            uniqueNodes = []
            uniquePathObjects = []
            for path in paths:
                if path.source in uniqueNodes:
                    continue
                uniqueNodes.append(path.source)
                uniquePathObjects.append(path)
            print("\nUnique values of Key "+markedSet[i]+": ")
            for u in uniquePathObjects:
                minimum_paths.append(u.path)
                total_cost += u.cost
                print(u.source, u.cost, u.path)

            #storing the cost in SP matrix
            for j in range(0,uniquePathObjects.__len__()):
                ind = markedSet.index(uniquePathObjects[j].source)
                SP[ind][i] = uniquePathObjects[j].cost

    print("\n\n")
    print("SP matrix: \n")
    for i in range(0,k+1):
        print(SP[i])

    g = FindMST.Graph(k+1)
    for i in range(0,k+1):
        for j in range(0,k+1):
            if SP[j][i] > 0:
               g.addEdge(i,j,SP[j][i])

    result = g.KruskalMST()
    TreeMIN = [[0 for j in range(k+1)] for i in range(k+1)]
    for u,v,weight in result:
        TreeMIN[u][v] = weight

    new_marked_set = markedSet
    new_marked_set.append('0')
    new_list = []
    vertices = set()
    for i in range(len(TreeMIN)):
        for j in range(len(TreeMIN[i])):
            if TreeMIN[i][j] != 0:
                for o in minimum_paths:
                    if new_marked_set[i] == o[-1] and new_marked_set[j] == o[0]:
                        new_list.append(o)
                        for x in o:
                            vertices.add(x)
                            vertices.add(x)
            if TreeMIN[i][j] >= maxLength:
                temp = [new_marked_set[j], new_marked_set[i]]
                new_list.append(temp)
                vertices.add(new_marked_set[j])
                vertices.add(new_marked_set[i])




    print("\n\n")

    print("MST matrix: \n")
    print("   14, 15, 20, 23, 25, 27, 29, 38")


    for i in range(0,k+1):
        print(new_marked_set[i], TreeMIN[i])

    pprint(new_list)
    print("\n")
    print(total_cost)
    return new_list, TreeMIN, vertices


###################################################################################

def find_expanded_paths(graph_paths, TreeMIN, vertices, graphDb):
    vert = sorted(list(vertices))
    k = len(vert)
    graph = [[0 for j in range(k)] for i in range(k)]

    count = 0
    for i in range(len(graph_paths)):
        for j in range(len(graph_paths[i])-1):
            count +=1
            column = vert.index(graph_paths[i][j])
            row = vert.index(graph_paths[i][j+1])
            if row == 0:
                graph[row][column] = 5.32
            else:
                graph[row][column] = math.log((graphDb.getNumberOfNeighbors(vert[row])+1), 2)
            print(vert[row], vert[column])
    print("Hello")
    pprint(graph)
    g = FindMST.Graph(k)

    for i in range(0, k):
        for j in range(0, k):
            if graph[i][j] > 0:
                g.addEdge(i, j, graph[i][j])

    result = g.KruskalMST()
    mst = [[0 for j in range(k+1)] for i in range(k+1)]
    pprint(result)
    for u, v, weight in result:
        mst[u][v] = weight
    pprint(mst)
    return mst,vert

def dynamic_incrementation(mst, new_marked_nodes, original_marked_nodes, lengths, original_marked_paths, vertices):
    print("\n\nVertices:", type(vertices))
    graphDb = dbWriter.DirectedGraph("bolt://127.0.0.1:7687")
    nodes = graphDb.getAllNodes()
    maxLength = math.log((nodes.__len__()),2)


    terminals = new_marked_nodes
    markedPaths = dict()
    for i in range(0,terminals.__len__()):

        hops = 0
        seed = terminals[i]
        costSeed = lengths[int(seed)-1]
        hops = hops + costSeed

        ids = []
        costs = []
        paths = []

        neighs = graphDb.getNeighboringNodes(seed)
        for j in range(0,neighs.__len__()):
            path = [seed,neighs[j]]
            ids.append(neighs[j])
            costs.append(lengths[int(neighs[j])-1])
            paths.append(path)
            addMarkedPath(markedPaths, neighs[j], seed, hops, path)

        minCost = min(costs)
        costs[:] = [x - minCost for x in costs]
        hops = hops + minCost

        while(hops <= maxLength):
            ind = [index for index, value in enumerate(costs) if value == 0]
            for j in range(0,ind.__len__()):
                expandNode = ids[ind[j]]
                neighs = graphDb.getNeighboringNodes(expandNode)

                for k in range(0,neighs.__len__()):
                    path = paths[ind[j]]

                    temp = [index for index, value in enumerate(path) if value == neighs[k]]
                    if(temp.__len__()>0):
                        continue
                    else:
                        path1 = []
                        for p in range(0, path.__len__()):
                            path1.append(path[p])
                        path1.append(neighs[k])
                        path = path1
                        ids.append(neighs[k])
                        costs.append(lengths[int(neighs[k])-1])
                        paths.append(path)
                        addMarkedPath(markedPaths,neighs[k],seed,hops,path)

            ids = [z for x,z in enumerate(ids) if x not in ind]
            costs = [z for x,z in enumerate(costs) if x not in ind]
            paths = [z for x,z in enumerate(paths) if x not in ind]

            minCost = min(costs)
            costs[:] = [x - minCost for x in costs]
            hops = hops + minCost

    print("Marked Paths:")
    new_marked_paths = original_marked_paths
    new_marked_set = sorted(list(vertices) + new_marked_nodes)
    new_marked_set = new_marked_set[1:len(new_marked_set)]
    print(new_marked_set)
    for x in markedPaths:
        if x not in original_marked_paths:
            new_marked_paths[x] = []
        for p in markedPaths[x]:
            new_marked_paths[x].append(p)

    minimum_paths, TreeMin, vertices = findMST(new_marked_paths, new_marked_set, graphDb, maxLength)
    pprint(minimum_paths)

    find_expanded_paths(minimum_paths, [], vertices, 0)

def dynamic_nodes(mst,new_marked_set,marked_set,lengths,vert,markedPaths):
    graphDb = dbWriter.DirectedGraph("bolt://127.0.0.1:7687")
    nodes = graphDb.getAllNodes()
    maxLength = math.log((nodes.__len__()), 2)
    cost_of_graph = 0
    for i in range(0, new_marked_set.__len__()):
        nid = new_marked_set[i];
        hops = 0
        seed = new_marked_set[i]
        costSeed = lengths[int(seed) - 1]
        hops = hops + costSeed

        ids = []
        costs = []
        paths = []

        neighs = graphDb.getNeighboringNodes(seed)
        for j in range(0, neighs.__len__()):
            path = [seed, neighs[j]]
            ids.append(neighs[j])
            costs.append(lengths[int(neighs[j]) - 1])
            paths.append(path)
            addMarkedPath(markedPaths, seed, neighs[j], hops, path)

        minCost = min(costs)
        costs[:] = [x - minCost for x in costs]
        hops = hops + minCost

        while (hops <= maxLength):
            ind = [index for index, value in enumerate(costs) if value == 0]
            for j in range(0, ind.__len__()):
                expandNode = ids[ind[j]]
                neighs = graphDb.getNeighboringNodes(expandNode)

                for k in range(0, neighs.__len__()):
                    path = paths[ind[j]]

                    temp = [index for index, value in enumerate(path) if value == neighs[k]]
                    if (temp.__len__() > 0):
                        continue
                    else:
                        path1 = []
                        for p in range(0, path.__len__()):
                            path1.append(path[p])
                        path1.append(neighs[k])
                        path = path1
                        ids.append(neighs[k])
                        costs.append(lengths[int(neighs[k]) - 1])
                        paths.append(path)
                        addMarkedPath(markedPaths, seed, neighs[k], hops, path)
            ids = [z for x, z in enumerate(ids) if x not in ind]
            costs = [z for x, z in enumerate(costs) if x not in ind]
            paths = [z for x, z in enumerate(paths) if x not in ind]

            #print (paths)
            minCost = min(costs)
            costs[:] = [x - minCost for x in costs]
            hops = hops + minCost

        k = len(vert)+1
        graph = [[0 for j in range(k)] for i in range(k)]
        print("MST")
        pprint(mst)
        print(k)
        g = FindMST.Graph(k)
        for i in range(0, k-1):
            for j in range(0, k-1):
                if mst[i][j] > 0:
                    g.addEdge(i, j, mst[i][j])

        newpaths=markedPaths.get(nid)

        for route in newpaths:
            path=route.path
            for vertex in path:
                if vertex in vert:
                    g.addEdge(vert.index(vertex), k-1, math.log((graphDb.getNumberOfNeighbors(vertex)+1), 2))
        unmarked_set=list(set(vert)-set(marked_set))
        result = g.KruskalMST()
        mst = [[0 for j in range(k)] for i in range(k)]
        pprint(result)
        for u, v, weight in result:
            if weight != 5.32:
                cost_of_graph += weight
            mst[u][v] = weight

        for u in unmarked_set:
            count=0
            for v in range(len(vert)):
                if mst[int(vert.index(u))][v]>0 or mst[v][int(vert.index(u))]>0:
                    count=count+1
            print(u)
            if count<2:
                print (u)
        vert.append(nid)
        pprint(mst)
        print("cost", cost_of_graph)
    return mst,vert

def main():
    graphDb = dbWriter.DirectedGraph("bolt://127.0.0.1:7687")
    nodes = graphDb.getAllNodes()
    #graphDb.clearGraph();

    terminals = ['21','15','20','23','25','27','29','38'];
    new_marked_set=['14','36','17']
    lengths = [0]* nodes.__len__()
    for i in graphDb.getAllNodes():
        lengths[int(i)-1] = math.log((graphDb.getNumberOfNeighbors(i)+1),2)
    #print(lengths)
    maxLength = math.log((nodes.__len__()),2)
    markedPaths = dict()
    for i in range(0,terminals.__len__()):

        hops = 0
        seed = terminals[i]
        costSeed = lengths[int(seed)-1]
        hops = hops + costSeed

        ids = []
        costs = []
        paths = []

        neighs = graphDb.getNeighboringNodes(seed)
        for j in range(0,neighs.__len__()):
            path = [seed,neighs[j]]
            ids.append(neighs[j])
            costs.append(lengths[int(neighs[j])-1])
            paths.append(path)
            addMarkedPath(markedPaths, neighs[j], seed, hops, path)

        minCost = min(costs)
        costs[:] = [x - minCost for x in costs]
        hops = hops + minCost

        while(hops <= maxLength):
            ind = [index for index, value in enumerate(costs) if value == 0]
            for j in range(0,ind.__len__()):
                expandNode = ids[ind[j]]
                neighs = graphDb.getNeighboringNodes(expandNode)

                for k in range(0,neighs.__len__()):
                    path = paths[ind[j]]

                    temp = [index for index, value in enumerate(path) if value == neighs[k]]
                    if(temp.__len__()>0):
                        continue
                    else:
                        path1 = []
                        for p in range(0, path.__len__()):
                            path1.append(path[p])
                        path1.append(neighs[k])
                        path = path1
                        ids.append(neighs[k])
                        costs.append(lengths[int(neighs[k])-1])
                        paths.append(path)
                        addMarkedPath(markedPaths,neighs[k],seed,hops,path)

            ids = [z for x,z in enumerate(ids) if x not in ind]
            costs = [z for x,z in enumerate(costs) if x not in ind]
            paths = [z for x,z in enumerate(paths) if x not in ind]

            minCost = min(costs)
            costs[:] = [x - minCost for x in costs]
            hops = hops + minCost

    print("Marked Paths:")
    for k,v in markedPaths.items():
        print("Key:" + k)
        for v1 in v:
            print(v1.source, v1.cost, v1.path)

    print("\n")

    minimum_paths, TreeMin, vertices = findMST(markedPaths, terminals, graphDb, maxLength)

    mst,vert = find_expanded_paths(minimum_paths, TreeMin, vertices, graphDb)
    mst,vert = dynamic_nodes(mst,new_marked_set,terminals,lengths,vert,markedPaths)
    #dynamic_incrementation([10,20,30], ['16', '10', '18'], terminals, lengths, markedPaths, vertices)

    #############################################################################

if __name__ == "__main__":
    main()
