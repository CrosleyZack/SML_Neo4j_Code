import dbWriter
import math
import FindMST

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

def findMST(markedPaths, markedSet, graphDB):
    k = markedSet.__len__()
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
    
    print("\n\n")
    print("MST matrix: \n")
    for i in range(0,k+1):
        print(TreeMIN[i])


###################################################################################

def main():
    graphDb = dbWriter.DirectedGraph("bolt://127.0.0.1:7687")
    nodes = graphDb.getAllNodes()
    #graphDb.clearGraph();
    
    terminals = ['14','15','20','23','25','27','29','38'];
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

findMST(markedPaths,terminals,graphDb)

#############################################################################

if __name__ == "__main__":
    main()
