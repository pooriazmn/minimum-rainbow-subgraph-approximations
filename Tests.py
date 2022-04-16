import Graph as G
import math as m
import random
import os
from statistics import mean
from Koch2011 import Koch2011
from tirodkar import Tirodkar2017
from schiermeyer2013 import Schiermeyer2013


def generateTestData(startGraph, numGraphs):
    #start with the initial graph
    graphs = []
    graphs.append(startGraph)

    #generate a sequence of random graphs
    for i in range(numGraphs):
        graphs.append(G.randomGraph(graphs[i]))
    return graphs

def writeTestData(testData, fileName):
    graphs = testData[0]
    size = testData[1]
    density = testData[2]
    maxColour = testData[3]

    testDataString = str(size) + "," + str(density) + "," + str(maxColour) + "#\n"
    #create a string for each test graph
    for graph in graphs:

        #write each edge
        for edge in graph.edges:
            testDataString += str(graph.vertices.index(edge.v1)) + "," + str(graph.vertices.index(edge.v2)) + "," + str(edge.colour) + "\n"
        testDataString += "#" #between the graphs
    
    #write to the file
    file = open(fileName, "w")
    file.write(testDataString)
    file.close()

def readTestData(fileName):
    #open the file containing the test data
    file = open(fileName, "r")
    testDataString = file.read()
    file.close()

    graphs = []

    #split the string into the strings for each test
    testDataStrings = testDataString.split("#")
    params = testDataStrings[0].split(",")
    size = int(params[0])
    density = int(params[1])
    maxColour = int(params[2])

    #parse the string for each test into a graph object
    for i in range(1, len(testDataStrings)):
        testString = testDataStrings[i]

        if len(testString) > 0:
            graphData = testString.split("\n")

            newGraph = G.Graph(maxColour)
            #create the vertices
            for i in range(size):
                newGraph.newVertex()

            #create the edges
            for i in range(0, len(graphData)):
                edgeStr = graphData[i]
                if len(edgeStr) > 0:
                    indices = edgeStr.split(",")
                    newGraph.addEdge(newGraph.vertices[int(indices[0])], newGraph.vertices[int(indices[1])], int(indices[2]))

            graphs.append(newGraph)

    return [graphs, size, density, maxColour]

def runTest(testData, mrsFunction, draw=False):
    results = []

    graphs = testData[0]
    size = testData[1]
    density = testData[2]
    maxColour = testData[3]
    for graph in graphs:
        if(draw):
            print("drawing original graph")
            graph.draw()
        resultGraph = mrsFunction(graph)

        if(draw):
            print("drawing rainbow subgraph")
            resultGraph.draw()
        
        results.append(resultGraph.n())

    return [results, size, density, maxColour]

def runTestFromFile(testFile, mrsFunction, draw=False):
    return runTest(readTestData(testFile), mrsFunction, draw=draw)

sizes = [10, 50, 100, 200, 500, 1000]
def generateStartingGraphs():
    graphs = []

    #walk through all sizes
    for size in sizes:
        #walk through all edge densities
        for edgeDensity in range(10, 90, 10):
            edgeDensityFraction = edgeDensity / 100
        
            #figure out what the colour parameters will be
            maxColours = int(m.sqrt(size))
            if(maxColours < 5):
                maxColours = 5
            colourStep = m.ceil((maxColours - 5) / 5)
            if colourStep < 1:
                colourStep = 1

            #walk through the numbers of colours
            for numColours in range(5, maxColours + colourStep, colourStep):
                #generate the vertices of the graph
                newGraph = G.Graph(numColours)
                for i in range(size):
                    newGraph.newVertex()

                #generate the edges
                for u in newGraph.vertices:
                    for v in newGraph.vertices:
                        edgeProbability = random.random()
                        if edgeProbability < edgeDensityFraction:
                            newGraph.addEdge(u, v, 0)

                #generate the colours
                toBeColoured = newGraph.edges.copy()
                colourNum = 0
                while len(toBeColoured) > 0:
                    edgeIndex = random.randint(0, len(toBeColoured)-1)
                    edge = toBeColoured[edgeIndex]
                    edge.colour = colourNum
                    toBeColoured.remove(edge)
                    colourNum = (colourNum + 1) % numColours

                #ensure that the colouring is proper
                for v in newGraph.vertices:
                    #categorize all the edges incident to v by which neighbour they connect v to
                    neighbours = {}
                    for edge in v.incidentEdges:
                        if edge.v1 == v:
                            u = edge.v2
                        else:
                            u = edge.v1

                        if not u in neighbours.keys():
                            neighbours[u] = [edge]
                        else:
                            neighbours[u].append(edge)

                    #see if there are two edges of the same colour between two v and any of its neighbours
                    for u in neighbours.keys():
                        edges = neighbours[u]
                        colourClasses = {}
                        for edge in edges:
                            if not edge.colour in colourClasses.keys():
                                colourClasses[edge.colour] = edge
                            #if this colour is a repeat, find an available colour to change this colour to
                            else:
                                for i in range(numColours-1, -1, -1):
                                    if not i in colourClasses.keys():
                                        edge.colour = i

                                assert(not edge.colour in colourClasses.keys())
                                assert(edge.colour < numColours)

                print("start graph with size=" + str(size) + ", density = " + str(edgeDensity) + ", and num colours = " + str(numColours) + " generated.")
                graphs.append([newGraph, size, edgeDensity, numColours])
    return graphs

def generateTests():
    startGraphs = generateStartingGraphs()
    for startGraph in startGraphs:
        graphs = generateTestData(startGraph[0], 10)
        fileName = "./Tests/TEST_" + str(startGraph[1]) + "_" + str(startGraph[2]) + "_" + str(startGraph[3]) + ".txt"
        writeTestData([graphs, startGraph[1], startGraph[2], startGraph[3]], fileName)
        print("Test data with size = " + str(startGraph[1]) + ", density = " + str(startGraph[2]) + ", num colours = " + str(startGraph[3]) + " generated")
    pass

#will run all generated tests on graphs of size sizeMin to sizeMax (inclusive) and write the results to the results csv
#mrsFunctions should be a list of functions that accept exactly one parameter (the graph) and returns exactly a rainbow subgraph
def runTests(mrsFunctions, sizeMin=10, sizeMax=1000):
    for size in sizes:
        if size >= sizeMin and size <= sizeMax:
            for edgeDensity in range(10,90,10):
                #figure out what the colour parameters will be
                maxColours = int(m.sqrt(size))
                if(maxColours < 5):
                    maxColours = 5
                colourStep = m.ceil((maxColours - 5) / 5)
                if colourStep < 1:
                    colourStep = 1

                #walk through the numbers of colours
                for numColours in range(5, maxColours + colourStep, colourStep):
                    fileName = "./Tests/TEST_" + str(size) + "_" + str(edgeDensity) + "_" + str(numColours) + ".txt"
                    if os.path.isfile(fileName):
                        for mrsFunction in mrsFunctions:
                            results = runTestFromFile(fileName, mrsFunction)
                            resultString = mrsFunction.__name__
                            resultString += "," + str(results[1])
                            resultString += "," + str(results[2])
                            resultString += "," + str(results[3])
                            for val in results[0]:
                                resultString += "," + str(val)
                            resultString += "\n"
                            resultFile = open("results-koch.csv", "a")
                            resultFile.write(resultString)
                            resultFile.close()

def produceAnalysis(fileNames):
    for fileName in fileNames:
        file = open(fileName, "r")
        resultString = file.read()
        file.close()

        name = None
        resultsBySize = {}
        resultsByDensity = {}
        resultsByColours = {}

        experiments = resultString.split("\n")
        for experiment in experiments:
            if len(experiment) > 0:
                vals = experiment.split(",")
                if name is None:
                    name = vals[0]

                size = int(vals[1])
                density = int(vals[2])
                num_colours = int(vals[3])

                if not size in resultsBySize.keys():
                    resultsBySize[size] = []
                if not density in resultsByDensity.keys():
                    resultsByDensity[density] = []
                if not num_colours in resultsByColours.keys():
                    resultsByColours[num_colours] = []

                for i in range(4, len(vals)):
                    resultsBySize[size].append(int(vals[i]))
                    resultsByDensity[density].append(int(vals[i]))
                    resultsByColours[num_colours].append(int(vals[i]))

        #write the results for analysis by size
        for size in resultsBySize.keys():
            avgBySize = mean(resultsBySize[size])
            analysisFile = open("results-analysis-size.csv", "a")
            analysisFile.write(name + "," + str(size) + "," + str(avgBySize))
            analysisFile.write("\n")
            analysisFile.close()

        #write the results for analysis by density
        for density in resultsByDensity.keys():
            avgByDensity = mean(resultsByDensity[density])
            analysisFile = open("results-analysis-density.csv", "a")
            analysisFile.write(name + "," + str(density) + "," + str(avgByDensity))
            analysisFile.write("\n")
            analysisFile.close()

        #write the results for analysis by number of colours
        for numColours in resultsByColours.keys():
            avgByColours = mean(resultsByColours[numColours])
            analysisFile = open("results-analysis-colours.csv", "a")
            analysisFile.write(name + "," + str(numColours) + "," + str(avgByColours))
            analysisFile.write("\n")
            analysisFile.close()

                
                

if __name__ == "__main__":
    produceAnalysis(["results-koch.csv", "results-schiermeyer.csv", "results-tirodkar.csv"])