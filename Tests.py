import Graph as G
import math as m
import random
import os
import multiprocessing
import threading
from statistics import mean
from Koch2011 import Koch2011
from tirodkar import Tirodkar2017
from schiermeyer2013 import Schiermeyer2013


def generateTestData(startGraph, numGraphs):
    graphs = []
    # start with the initial graph
    graphs.append(startGraph)

    # generate a sequence of random graphs
    for i in range(numGraphs):
        graphs.append(G.randomGraph(graphs[i]))
    return graphs

def writeTestData(testData, fileName):
    graphs = testData[0]
    size = testData[1]
    density = testData[2]
    maxColour = testData[3]

    testDataString = str(size) + "," + str(density) + "," + str(maxColour) + "#\n"
    # create a string for each test graph
    for graph in graphs:

        # write each edge
        for edge in graph.edges:
            testDataString += str(edge.v1.index) + "," + str(edge.v2.index) + "," + str(edge.colour) + "\n"
        testDataString += "#" # between the graphs
    
    #write to the file
    file = open(fileName, "w")
    file.write(testDataString)
    file.close()


def readTestData(fileName):
    # open the file containing the test data
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

    # parse the string for each test into a graph object
    for i in range(1, len(testDataStrings)):
        testString = testDataStrings[i]

        if len(testString) > 0:
            graphData = testString.split("\n")

            newGraph = G.Graph(maxColour)
            # create the vertices
            for i in range(size):
                newGraph.newVertex(i)

            # create the edges
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


def generateStartingGraph(size, density, maxColour):
    edgeDensityFraction = density / 100

    # generate the vertices of the graph
    newGraph = G.Graph(maxColour)
    for _ in range(size):
        newGraph.newVertex()

    # generate the edges
    for u in newGraph.vertices.values():
        for v in newGraph.vertices.values():
            if u is v or v in u.neighbours:  # no self edges or multiple edges
                continue
            edgeProbability = random.random()
            if edgeProbability < edgeDensityFraction:
                newGraph.addEdge(u, v, 0)

    # generate the colours
    toBeColoured = newGraph.edges.copy()
    colourNum = 0
    while len(toBeColoured) > 0:
        edgeIndex = random.randint(0, len(toBeColoured)-1)
        edge = toBeColoured[edgeIndex]
        edge.colour = colourNum
        toBeColoured.remove(edge)
        colourNum = (colourNum + 1) % maxColour

    print("start graph with size=" + str(size) + ", density = " + str(density) + ", and num colours = " + str(maxColour) + " generated.")
    return newGraph

def generateTest(size, density, maxColour):
    startGraph = generateStartingGraph(size, density, maxColour)
    graphs = generateTestData(startGraph, 10)
    print("Test data with size = " + str(size) + ", density = " + str(density) + ", num colours = " + str(maxColour) + " generated")
    writeTestData([graphs, size, density, maxColour], "Tests/TEST_" + str(size) + "_" + str(density) + "_" + str(maxColour) + ".txt")

sizes = [10, 50, 100, 200, 500, 1000]
def generateTests(size):
    #walk through all edge densities
    densityMin = 10

    if size == 200:
        thread = threading.Thread(target=generateTest, args=(200,50,11,))
        thread.start()
        densityMin = 60
    
    for edgeDensity in range(densityMin, 90, 10):
        
        #figure out what the colour parameters will be
        maxColours = int(m.sqrt(size))
        if(maxColours < 5):
            maxColours = 5
        colourStep = m.ceil((maxColours - 5) / 5)
        if colourStep < 1:
            colourStep = 1

        #walk through the numbers of colours
        for numColours in range(5, maxColours + colourStep, colourStep):
            thread = threading.Thread(target=generateTest, args=(size, edgeDensity, numColours,))
            thread.start()

#will run all generated tests on graphs of size sizeMin to sizeMax (inclusive) and write the results to the results csv
#mrsFunction should be a function that accepts exactly one parameter (the graph) and returns exactly a rainbow subgraph
def runTests(mrsFunction, outputFile, sizeMin=10, sizeMax=1000):
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
                        results = runTestFromFile(fileName, mrsFunction)
                        resultString = mrsFunction.__name__
                        resultString += "," + str(results[1])
                        resultString += "," + str(results[2])
                        resultString += "," + str(results[3])
                        for val in results[0]:
                            resultString += "," + str(val)
                        resultString += "\n"
                        resultFile = open(outputFile, "a")
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
    tests_200 = multiprocessing.Process(target=generateTests, args=(200,))
    tests_500 = multiprocessing.Process(target=generateTests, args=(500,))
    tests_1000 = multiprocessing.Process(target=generateTests, args=(1000,))

    tests_200.start()
    tests_500.start()
    tests_1000.start()