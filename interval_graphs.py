#!/sr/bin/env python3
# -*- codinneighbors: utf-8 -*-

"""Interval graphs algorithm implementation"""

__author__ = 'Ioanna Ntousaki'
__version__ = '3.10.11'

from sys import argv
from collections import deque
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("task", help = "Assign task to the algorithm: 'lexbfs' 'chordal' 'interval'") 
parser.add_argument("input_filename", help = "A .txt input file with the neighbor nodes of a graph in pairs")
args = parser.parse_args()

# read a .txt file containing the graph neighbors, one pair per line 
def getNeighbors():
    neighbors = {}  # dictionary: {key : value} = {node : neighbors}
    with open(args.input_filename, "r") as file:
        for line in file:
            # Split line and convert line parts to integers.
            try:
                x, y = line.split()
                # when a new node appears, create a new key in the dictionary
                # with an empty list as its value
                if int(x) not in neighbors:
                    neighbors[int(x)] = []
                if int(y) not in neighbors:
                    neighbors[int(y)] = []
                # add the nodes in the neighbor's list
                neighbors[int(x)].append(int(y))
                neighbors[int(y)].append(int(x))
            except:
                # when a non-valid line, ignore it
                continue
    return neighbors
    
            
# find the lexicograph order of the graph
def findLexOrder(neighbors):
    visitNodes = deque()
    visitNodes.append(deque([x for x in range(len(neighbors))]))
    s = visitNodes[0].popleft()   # the first node to visit
    lexOrder = deque()
    # start forming lexicograph order from the first node
    visitNodes.insert(0, deque([s]))
    
    # while there are still nodes that need to be ordered
    while len(visitNodes) > 0:
        u = visitNodes[0][0]
        visitNodes[0].popleft()
        position = 0
        countNeighbours = 0 # counting every time the neighbors that we have found for the specific node 
        while position < len(visitNodes) and countNeighbours < len(neighbors[u]):
            changeNodesPosition = deque()   # contains the neighbors that are found in the visitNodes[position] deque
            for neighbor in neighbors[u]:
                if neighbor in visitNodes[position]:
                    visitNodes[position].remove(neighbor)
                    changeNodesPosition.append(neighbor)
                    countNeighbours += 1
            if changeNodesPosition:
                visitNodes.insert(position, changeNodesPosition)
            position += 1

        lexOrder.append(u)
        visitNodes = deque(x for x in visitNodes if x)  # remove empty deques
    return lexOrder

# decide if the graph given is chordal or not
def isChordal(lexOrder, neighbors):
    lexOrder.reverse()  # reverse the order of the lexographical search output
    # execute the repetition for each node based on reversed lexOrder except the last one 
    for i in range(len(lexOrder)-1):
        nodeNeighbors = deque()
        # check all the following nodes based on reversed lexOrder and keep only the neighbors in nodeNeighbors
        for j in range(i+1, len(lexOrder)):
            if lexOrder[j] in neighbors.get(lexOrder[i]):
                # for the first neighbor that follows keep
                # its neighbors in the neighborsOfNeighbor deque
                if not (nodeNeighbors): 
                    neighborsOfNeighbor = deque()
                    for k in range(j+1, len(lexOrder)):
                        if lexOrder[k] in neighbors.get(lexOrder[j]):
                            neighborsOfNeighbor.append(lexOrder[k])
                nodeNeighbors.append(lexOrder[j])
        nodeNeighbors.popleft()
        # if the node's neighbors are not a sub-set of the neighbor's neighbors, the graph is not chordal, so stop 
        if not (all(item in neighborsOfNeighbor for item in nodeNeighbors)):
            return False
    return True

# execute bfs in a graph and store the connected components of it into a table using a dictionary
def bfs(graph, node, start):
    global components
    global componentsAdd
    global C
    queue = deque()
    visited = [False] * len(graph) 
    inqueue = [False] * len(graph)
    nodeIndex = list(graph).index(node)
    queue.appendleft(node)
    inqueue[nodeIndex] = True
    keepNodes = [] # a list with the connected components of the graph
    while not (len(queue) == 0):
        firstInQ = queue.pop()
        inqueue[list(graph).index(firstInQ)] = False
        visited[list(graph).index(firstInQ)] = True
        keepNodes.append(firstInQ)
        for v in graph[firstInQ]:
            vIndex = list(graph).index(v)
            # add each neighbor that has not been visited into the queue
            if not visited[vIndex] and not inqueue[vIndex]:
                queue.appendleft(v)
                inqueue[vIndex] = True
        # queue is empty, so the component is complete
        if not queue:
            # search the dict for the specific component
            # if it doesn't exist, create a new key-value pair with value the list of the new component
            if keepNodes not in components.values():
                componentsAdd += 1
                components[componentsAdd] = keepNodes
                key = componentsAdd
            else:
                # if the component already in the dictionary, find its key
                for key in components.keys():
                    if components[key] == keepNodes:
                        break
            # put the associated key into the appropriate position in C
            for i in keepNodes:
                C[start][i] = key

            # when there is a node not visited and is
            # not connected to the previous ones, add it to the queue and empty the components table
            if False in visited:
                node = list(graph)[visited.index(False)]
                queue.appendleft(node)
                inqueue[visited.index(False)] = True
                keepNodes = []

# decide whether the graph is interval or not 
def is_AT_free(graph, lexOrder):
    
    global C
    #   if the graph is not chordal, it cannot be interval
    if not isChordal(lexOrder, neighbors):
        return False

    for node in graph:
        conn_Component = {}
        # execute bfs into connected component sub-graph
        # x refers to the subgraph
        for x in graph:
            # create sub-graph by excluding the node and its neighbors
            if x not in graph[node] and x != node:
                conn_Component[x] = [y for y in graph[x]
                                    if (y not in graph[node] and y != node)]
        # if the node is connected with everything, there will be no values in conn_Component dict
        if conn_Component: 
            bfs(conn_Component, list(conn_Component.keys())[0], node)
    # search the table C for similar values (excluding zero values/neighbors) between x,y,z combination pairs 
    # if there is at least one such combination, the graph is not interval
    for x in range(len(C)):
        for y in range(len(C)):
            for z in range(len(C)):
                if C[x][y] != 0 and C[x][z] != 0 and C[y][x] != 0 and C[y][z] != 0 and C[z][x] != 0 and C[z][y] != 0:
                    if C[x][y] == C[x][z] and C[y][x] == C[y][z] and C[z][x] == C[z][y]:
                        return False
    return True


if __name__ == '__main__':
       
        try:
            neighbors = getNeighbors()  # create graph                            
        except FileNotFoundError as fnf_error:
            print(fnf_error)
        lexOrder = findLexOrder(neighbors)  # get lexicograph search output
         # call the right function according to the user input
        if args.task.strip() == 'lexbfs':
            print(list(lexOrder))
        elif args.task.strip() == 'chordal':
            print(isChordal(lexOrder, neighbors))
        elif args.task.strip() == 'interval':
            C = [[0]*len(neighbors) for x in range(len(neighbors))]
            componentsAdd = 0
            components = {}
            print(is_AT_free(neighbors, lexOrder))
        else:
            raise Exception() # throw an exception in order for the program to print the help message 
    