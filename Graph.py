import random
import networkx as nx
from matplotlib import pyplot as plt

class Vertex:
    #create a vertex
    def __init__(self):
        self.incidentEdges = []

    #check how many edges this vertex is incident to
    def degree(self):
        return len(self.incidentEdges)

    #add a new edge we are incident to
    def addEdge(self, newEdge):
        assert(newEdge.v1 == self or newEdge.v2 == self)
        self.incidentEdges.append(newEdge)

class Edge:
    #create an edge between v1 and v2 with a specific colour
    def __init__(self, v1, v2, colour):
        self.v1 = v1
        self.v2 = v2
        self.colour = colour

class Graph:
    #create an empty graph
    def __init__(self):
        self.vertices = []
        self.edges = []
        self.maxColour = -1

    #get the number of vertices in a graph
    def n(self):
        return len(self.vertices)

    def m(self):
        return len(self.edges)

    #add a new vertex to the graph
    def newVertex(self):
        self.vertices.append(Vertex())

    #add an existing vertex to the graph
    def addVertex(self, v):
        self.vertices.append(v)

    #connect vertices u and v with an edge of a specified colour
    def addEdge(self, u, v, colour):
        assert(u in self.vertices and v in self.vertices)
        newEdge = Edge(u, v, colour)
        self.edges.append(newEdge)
        u.addEdge(newEdge)
        v.addEdge(newEdge)

        if colour > self.maxColour:
            self.maxColour = colour


    def removeEdge(self, edge):
        self.edges.remove(edge)
        edge.v1.incidentEdges.remove(edge)
        edge.v2.incidentEdges.remove(edge)

    #check if vertices u and v are connected by at least one edge
    def adjacent(self, u, v):
        assert(u in self.vertices and v in self.vertices)
        for edge in self.edges:
            if (edge.v1 == u and edge.v2 == v) or (edge.v1 == v and edge.v2 == u):
                return True
        return False

    def toNX(self):
        nx_graph = nx.MultiGraph()

        for e in self.edges:
            nx_graph.add_edge(e.v1, e.v2, color=e.colour)

        return nx_graph

    def draw(self):
        selfNX = self.toNX()
        selfcolors = list(nx.get_edge_attributes(selfNX, name='color').values())
        nx.draw(selfNX, edge_color=selfcolors)
        plt.show()

    def copy(self):
        newGraph = Graph()
        vertices_map = {}
        for vertex in self.vertices:
            v = Vertex()
            vertices_map[vertex] = v
            newGraph.addVertex(v)

        for edge in self.edges:
            v1 = vertices_map[edge.v1]
            v2 = vertices_map[edge.v2]
            newGraph.addEdge(v1, v2, edge.colour)

        return newGraph


def rewire(G):
    newGraph = G.copy()
    m = newGraph.m()

    #find the first edge
    edgeNum = random.randint(0,m-1)
    edge = newGraph.edges[edgeNum]

    #find the first two vertices
    vertexNum = random.randint(0,1)
    if vertexNum == 0:
        u1 = edge.v1
        v = edge.v2
    else:
        u1 = edge.v2
        v = edge.v1

    vertexDegree = u1.degree()
    u2 = None

    #find the other edge and the associated vertices
    for e in newGraph.edges:
        if e.v1 != edge.v1 and e.v2 != edge.v2 and e.v2 != edge.v1 and e.v1 != edge.v2:
            if e.v1.degree() == vertexDegree:
                u2 = e.v1
                w = e.v2
                otherEdge = e
            elif e.v2.degree() == vertexDegree:
                u2 = e.v2
                w = e.v1
                otherEdge = e

        if not u2 is None:
            break

    if u2 is None:
        otherEdge = edge
        otherEdgeNum = 0
        while otherEdge == edge:
            otherEdge = newGraph.edges[otherEdgeNum]
            otherEdgeNum = (otherEdgeNum + 1) % m
        u2 = otherEdge.v1
        w = otherEdge.v2

    rewireAllowed = False
    while not rewireAllowed:
        #ensure that the rewire will not make the graph not proper
        rewireAllowed = True
        for incidentEdge in u1.incidentEdges:
            if incidentEdge != edge and (incidentEdge.v1 == w or incidentEdge.v2 == w) and incidentEdge.colour == edge.colour:
                edge.colour += 1
                rewireAllowed = False

        for incidentEdge in u2.incidentEdges:
            if incidentEdge != otherEdge and (incidentEdge.v2 == v or incidentEdge.v1 == v) and incidentEdge.colour == otherEdge.colour:
                incidentEdge.colour += 1
                rewireAllowed = False

    newGraph.removeEdge(edge)
    newGraph.removeEdge(otherEdge)

    newGraph.addEdge(u1, w, edge.colour)
    newGraph.addEdge(u2, v, otherEdge.colour)

    return newGraph

def randomGraph(G):
    k = G.m()
    newGraph = G.copy()

    for i in range(k):
        newGraph = rewire(newGraph)
    return newGraph
