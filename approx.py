from math import sqrt
import networkx as nx
import sys
import random
import time
import os

"""
TSP 2-Approximation Algorithm
1. Using Prim's algorithm to find the minimum spanning tree of the given graph. We 
   randomly choose a vertex as the node of tree.
2. Traversal each node in MST by DFS (pre-order traversal) which leads to a path L.
3. Transforming the path into a Hamiltonian cycle by connecting its tail and head.

"""

def cost(v1, v2):
    # This function calculates the distance between two vertices v1 and v2
    # The result is rounded to an integer
    return round(sqrt((v1["x"] - v2["x"]) ** 2 + (v1["y"] - v2["y"]) ** 2))


def Prim(vertices, root):
    # We implement Prim's algorithm to construct a Minimum Spanning Tree
    nodes = list(range(len(vertices)))  # Nodes number from 0 to N-1
    new_nodes = []  # The nodes list for tree
    mst_edges = []  # The edge set for MST
    # 1. Push the root node into the new_nodes list
    new_nodes.append(root)
    nodes.remove(root)
    # 2. Each iteration, we move a node v from nodes list to new_nodes list
    #    so that edge (u,v) has the minimum weight for any u in list new_node.
    #    The loop terminates when all vertices are moved from nodes to new_nodes.
    while len(nodes) != 0:
        cost_min = sys.maxsize  # Record the minimum weight edge
        for v in nodes:
            for u in new_nodes:
                cur = cost(vertices[u], vertices[v])    # The cost of current edge
                if cur < cost_min:  # Update edge (u_min,v_min) when current weight is smaller
                    u_min = u   
                    v_min = v
                    cost_min = cur
        # Move node v_min from nodes to new_nodes
        new_nodes.append(v_min)
        nodes.remove(v_min)
        mst_edges.append((u_min, v_min, cost_min))  # Add edge (u_min, v_min) to MST
    return mst_edges


def DFS(edges):
    # Pre-order traversal of a tree is used to construct a Hamiltonian cycle in the MST
    # We construct the graph by Graph() function in networkx package with edge set of the MST
    graph = nx.Graph()
    graph.add_weighted_edges_from(edges)
    start = 0   # We start from the root node of the MST
    dfs_path = list(nx.dfs_preorder_nodes(graph, edges[start][0]))  # Pre-order traversal of the MST
    return dfs_path


def distance(path, vertices):
    # In this function, we calculate the total distance of the tour
    dist = 0
    for i in range(len(path) - 1):
        dist += cost(vertices[path[i]], vertices[path[i+1]])
    dist += cost(vertices[path[-1]], vertices[path[0]]) # Add the distance between the starting point and the last one
    return dist


def mst_approx(file, cutoff,random_seed):
    # The main part of the mst approxiamtion algorithm
    # Set the random seed
    random.seed(random_seed)    

    # Reading input file and construct the graph
    vertices = []
    f = open(file, "r")
    content = f.readlines()
    for line in content:
        line = line.split()
        try:
            float(line[0])
        except (ValueError, IndexError):
            continue
        # The vertex information is stored in a dictionary including its x position
        # y position and vertex id. All vertices form a list.
        vertex = {"id": float(line[0]), "x": float(line[1]), "y": float(line[2])}
        vertices.append(vertex)
    f.close()

    root = random.randint(0, len(vertices)-1)   # Randomly choose a root to construct the MST
    start = time.time()   # Record the start time
    mst_edges = Prim(vertices, root)    # Construct MST from the root node
    tour = DFS(mst_edges)   # Get the Hamiltonian cycle by pre-order traversal of MST
    dist = distance(tour, vertices) # Calculate total distance of the tour
    end = time.time()   # Record the end time

    # Write results into trace and solution files
    base = os.path.basename(file)
    sol_file = base[:-4] + "_Approx" + "_" + str(cutoff) + "_" + str(random_seed) + ".sol"  # Name of solution file
    trace_file = base[:-4] + "_Approx" + "_" + str(cutoff) + "_" + str(random_seed) + ".trace"  # Name of trace file
    # Write running time and result distance into trace file
    trace = open("./output/" + trace_file, "w+")
    trace.write("%.2f, %d"%(end - start, dist))
    trace.close()
    # Write total distance and corresponding tour into solution file
    solution = open("./output/" + sol_file, "w+")
    solution.write(str(dist) + "\n")
    solution.write(",".join(str(i) for i in tour))
    solution.close()
