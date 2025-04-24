from collections import defaultdict
from queue import PriorityQueue

# graph class
class Graph: 
    """
    Making simple Graph class that uses adjancency list to store the nodes and edges
    """
    def __init__(self):
        self.__graph = defaultdict(list)

    def add_edge(self, u, v, weight, street_name):
        self.__graph[u].append((v, weight, street_name))
        self.__graph[v].append((u, weight, street_name))

    def get_graph(self):
        return self.__graph

# dijstra algorithm
def dijsktra_shortest_path(graph, start):
    paths = {vertex: [] for vertex in graph}
    paths[start] = [start]

    distances = {vertex: float("inf") for vertex in graph}
    distances[start] = 0 

    queue = PriorityQueue()
    queue.put((0, start))

    while not queue.empty():
        cd, cv = queue.get() 

        if cd > distances[cv]:
            continue 
            
        for n, w, s in graph[cv]:
            td = cd + w 
            
            if td < distances[n]:
                distances[n] = td 
                queue.put((td, n))
                paths[n] = paths[cv] + [n]

    return distances, paths 
