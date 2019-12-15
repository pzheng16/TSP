import math
import random
import time
from decimal import Decimal
import os
"""
TSP Hill Climbing Algorithm
"""

def getPosition(file):
    '''Read in the positioon of palces'''
    f = open(file, 'r')
    coordinates = []
    lineNum = 0
    for line in iter(f):
        lineNum += 1
        if (lineNum > 5):
            lineArr = line.strip().split(" ")
            try:
                x = float(lineArr[1])
                y = float(lineArr[2])
                coordinates.append((x, y))
            except:
                continue
    return coordinates

def getDistances(coordinates):
    '''Take two the coordiantes of two places, and calculate theri distance'''
    distances = {}
    for i, (x1 , y1) in enumerate(coordinates):
        for j , (x2 , y2) in enumerate(coordinates):
            distances[i, j] = math.sqrt((x1 - x2)**2+(y1 - y2)**2)
    return distances

# path : a 1-d array contain the index of the city along the path
def calPathDistances(path, distances):
    '''Calculate the total distance along a path'''
    total = 0
    for i in range(len(path) - 1):
        total += distances[path[i], path[i + 1]]

    #Because has to go back
    total += distances[path[-1], path[0]]
    return total

def genRandomPath(coordinates):
    '''Generate a random path along the coordinates'''
    path = []
    for i in range(len(coordinates)):
        path.append(i)

    random.shuffle(path)
    return path

def genRandomPairs(size):
    '''Create random pairs to switch in generating neighbors of current path'''
    x = list(range(size))
    y = list(range(size))
    random.shuffle(x)
    random.shuffle(y)
    for i in x:
        for j in y:
            yield(i, j)

def genNeighbor(path):
    '''Generate neighbor of the current path'''
    for i , j in genRandomPairs(len(path)):
        '''Only generate when i < j, because this could prevent from using same sequence as before'''
        if i < j:
            copy = path[:]
            '''Exchange i and j to get a neighbor'''
            copy[i], copy[j] = path[j], path[i]
            yield copy


def hillClimbing(filename, distances, cutOffTime, random_seed, coordinates):

    ''' Perform hillClimbing algorithm'''

    base = os.path.basename(filename)
    traceFile = open("./output/"+base[:-4] + "_LS1_" + str(cutOffTime) + "_" + str(random_seed) + ".trace", "a")

    startTime = time.time()

    ''' Maintain a global maximum '''
    globalScore = 1e20
    globalPath = []

    ''' Maintain a set to remember all the path, in order to prevent from going same path again'''
    path = set()

    while time.time() - startTime < cutOffTime:
        
        ''' If there is not move in last try, then restart by choosing another start point'''
        start = genRandomPath(coordinates)
        while tuple(start) in path:
            start = genRandomPath(coordinates)

        localPath = start

        localScore = int(calPathDistances(start, distances))

        while True:
            '''Use flag to store whether a movement is made during a loop'''
            flag = False
            for neighbor in genNeighbor(localPath):
                if time.time() - startTime > cutOffTime:
                    break

                '''Every calculation is a step'''
                neighborScore = int(calPathDistances(neighbor, distances))
                if neighborScore < localScore and (not (tuple(neighbor) in path)):

                    localScore = neighborScore
                    localPath = neighbor

                    ''' If localscore < globalscore, then update global score'''
                    if localScore < globalScore:

                        globalPath = localPath
                        globalScore = localScore
                        timeSoFar = time.time() - startTime
                        timeSoFar = Decimal(timeSoFar).quantize(Decimal("0.00"))
                        traceString = str(timeSoFar) + ", " + str(globalScore) + "\n"
                        traceFile.write(traceString)

                    flag = True
                    path.add(tuple(localPath))
                    break

            if flag == False:
                break

    traceFile.close()
    duration = time.time() - startTime
    return (globalScore, globalPath,duration)

def runHillClimbing(filename, cutoff_time, random_seed):
    random_seed = float(random_seed)
    cutoff_time = float(cutoff_time)
    random.seed(random_seed)
    
    coordinates = getPosition(filename)  # Read in data file
    distances = getDistances(coordinates)  # Compute all the distances
    result, bestPath,duration = hillClimbing(filename, distances, cutoff_time,random_seed, coordinates)

    base = os.path.basename(filename)
    solutionFile = open("./output/" + base[:-4] + "_LS1_" + str(cutoff_time) + "_" + str(random_seed)+".sol","w+")
    solutionFile.write(str(result) + "\n")
    
    # Output lists of points
    solutionPath = ",".join(str(index) for index in bestPath)
    solutionFile.write(solutionPath)
    solutionFile.close()

