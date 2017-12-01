import dbWriter
import math
import FindMST
import time
from pprint import pprint
import numpy as np
import random

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
            #print("\nUnique values of Key "+markedSet[i]+": ")
            for u in uniquePathObjects:
                minimum_paths.append(u.path)
                total_cost += u.cost
                #print(u.source, u.cost, u.path)

            #storing the cost in SP matrix
            for j in range(0,uniquePathObjects.__len__()):
                ind = markedSet.index(uniquePathObjects[j].source)
                SP[ind][i] = uniquePathObjects[j].cost

    #print("\n\n")
    #print("SP matrix: \n")
    #for i in range(0,k+1):
    #   print(SP[i])

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




    #print("\n\n")

    #print("MST matrix: \n")

    #for i in range(0,k+1):
    #    print(new_marked_set[i], TreeMIN[i])
    """
    pprint(new_list)
    print("\n")
    print(total_cost)
    """
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
            #print(vert[row], vert[column])

    #pprint(graph)
    g = FindMST.Graph(k)

    for i in range(0, k):
        for j in range(0, k):
            if graph[i][j] > 0:
                g.addEdge(i, j, graph[i][j])

    result = g.KruskalMST()
    mst = [[0 for j in range(k+1)] for i in range(k+1)]
    #pprint(result)
    for u, v, weight in result:
        mst[u][v] = weight
    #pprint(mst)
    h = len(mst)
    cost = 0;
    for i in range(h):
        for j in range(h):
            if mst[i][j] > 0:
                print (vert[i],vert[j],mst[i][j])
                cost = cost + mst[i][j]
    #print("cost", cost)
    return mst,vert,cost

terminals = ['102', '1193', '1186', '389', '1173', '1208', '454', '633', '1224', '753']
new_marked_set = ['555', '37', '434', '290', '628', '520', '33', '44', '534', '464', '323', '352', '612', '443', '274', '302', '605', '120', '676', '234', '132', '1672', '1234', '149', '152', '803', '646', '182', '711', '703', '773', '1121', '172', '237', '646', '155', '426', '133', '114', '115']

def main(iter):
    print("run",iter)
    graphDb = dbWriter.DirectedGraph("bolt://127.0.0.1:7687")
    nodes = graphDb.getAllNodes()
    #graphDb.clearGraph();

    for tp in range(iter):
        terminals.append(new_marked_set[tp])
    #print(len(terminals))
    lengths = [0]* nodes.__len__()*10
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
    
    minimum_paths, TreeMin, vertices = findMST(markedPaths, terminals, graphDb, maxLength)

    mst,vert,cost = find_expanded_paths(minimum_paths, TreeMin, vertices, graphDb)
    return cost
    
    #############################################################################

if __name__ == "__main__":
    time_list=[0]
    cost_list=[]
    for iter in range(len(new_marked_set)+1):
        start_time = time.time()
        cost = main(iter)
        time_list.append(time_list[iter]+time.time() - start_time)
        cost_list.append(cost)
    time_list.pop(0)
    print (time_list)
    print (cost_list)
    #print("--- %s seconds ---" % (time.time() - start_time))
