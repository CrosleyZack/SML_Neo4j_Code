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
        for mpath in value:
            if mpath.path == path:
                return
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

def dynamic_nodes(mst,new_marked_set,marked_set,lengths,vert,markedPaths):
    graphDb = dbWriter.DirectedGraph("bolt://127.0.0.1:7687")
    nodes = graphDb.getAllNodes()
    maxLength = math.log((nodes.__len__()), 2)
    cost_of_graph = 0
    unmarked = list(set(vert) - set(marked_set))
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
            path = [ neighs[j] ,seed]
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
                        path1.insert(0,neighs[k])
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
        newpaths=markedPaths.get(nid)
        edgelist=[]
        expand_set=[]
        for route in newpaths:
            path=route.path
            path.pop()
            intersect= list(set(path) & set(vert))
            if len(intersect)==1 and len(path)==1 :
                edgelist.append([vert.index(intersect[0]), k - 1, math.log((graphDb.getNumberOfNeighbors(intersect[0]) + 1), 2)])
            elif len(intersect)==2:
                umarked= list(set(intersect)& set(unmarked))
                marked = list(set(intersect) & set(marked_set))
                if len(umarked)==1:
                    edgelist.append([vert.index(umarked[0]), k - 1, math.log((graphDb.getNumberOfNeighbors(umarked[0]) + 1), 2)])
                elif len(marked)==1:
                    edgelist.append([vert.index(marked[0]), k - 1, math.log((graphDb.getNumberOfNeighbors(marked[0]) + 1), 2)])
            elif path[0] in vert:
                    if path[1] not in expand_set:
                        expand_set.append(path[1])
                    edgelist.append([k+expand_set.index(path[1]), k - 1, math.log((graphDb.getNumberOfNeighbors(path[1]) + 1), 2)])
                    edgelist.append([vert.index(path[0]), k + expand_set.index(path[1]), math.log((graphDb.getNumberOfNeighbors(path[0]) + 1), 2)])

        print(edgelist, expand_set)
        h = len(vert) + 1 + len(expand_set)
        print("MST")
        pprint(mst)
        print(h)
        d = FindMST.Graph(h)
        for i in range(0, k - 1):
            for j in range(0, k - 1):
                if mst[i][j] > 0:
                    d.addEdge(i, j, mst[i][j])
        for u,v,w in edgelist:
            d.addEdge(u,v,w)
        result = d.KruskalMST()
        mst = [[0 for j in range(h)] for i in range(h)]
        pprint(result)
        for u, v, weight in result:
            if weight != 5.32:
                cost_of_graph += weight
            mst[u][v] = weight

        vert.append(nid)
        for ele in expand_set:
            vert.append(ele)
            unmarked.append(ele)
        marked_set.append(nid)
        for u in unmarked:
            count = 0
            for v in range(len(vert)):
                if mst[int(vert.index(u))][v] > 0 or mst[v][int(vert.index(u))] > 0:
                    count = count + 1
            if count < 2:
                print("PSSSSS")
                uind = int(vert.index(u))
                for v in range(len(vert)):
                    mst[v].pop(uind)
                mst.pop(uind)
                vert.remove(u)
                unmarked.remove(u)
        pprint(mst)
        print("cost", cost_of_graph)
    return mst,vert

def main():
    graphDb = dbWriter.DirectedGraph("bolt://127.0.0.1:7687")
    nodes = graphDb.getAllNodes()
    #graphDb.clearGraph();

    terminals = ['21','36','23','25','27','29','38'];
    new_marked_set=['30','22','28']
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
    #############################################################################

if __name__ == "__main__":
    main()
