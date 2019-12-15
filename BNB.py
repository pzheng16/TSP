from math import sqrt
import numpy as np
import time
import os

"""
TSP Branch and Bound algorithm
"""

# calculate the second_smallest item in a list
def second_smallest(numbers):
    m1, m2 = float('inf'), float('inf')
    for x in numbers:
        if x <= m1:
            m1, m2 = x, m1
        elif x < m2:
            m2 = x
    return m2


# calculate Euclidean distance between two nodes
def distance(v1, v2):
    d1 = v2[1] * 1.0 - v1[1] * 1.0  # y2 - y1
    d2 = v2[0] * 1.0 - v1[0] * 1.0  # x2 - x1
    dis = sqrt(d1 ** 2 + d2 ** 2)
    return int(round(dis, 0))


# Read TSP files into a city matrix
class TSP_Read:
    def __init__(self):
        self.header = []
        self.matrix = []
        self.filename = ''
        self.number = ''

    def read_file(self, filename):
        f = open(filename, 'r')
        for i in range(5):
            self.header.append(f.readline())  # reads and stores the header section of the file
        line = f.readline()
        label = 0
        coordinates = [[]]
        while line != 'EOF':
            sp_line = line.split()
            if sp_line[0] == 'EOF':
                break
            label = int(sp_line[0])
            coordinates.append([float(sp_line[1]), float(sp_line[2])])
            line = f.readline()

        self.number = label
        self.filename = filename  # updates the filename
        self.matrix = [[0 for i in range(label + 1)] for j in range(label + 1)]
        self.matrix[0][0] = float('inf')
        for i in range(0, label + 1):
            for j in range(0, label + 1):
                if i == j:
                    self.matrix[i][j] = float('inf')
                elif i == 0 or j == 0:
                    self.matrix[i][j] = float('inf')
                else:
                    self.matrix[i][j] = distance(coordinates[i], coordinates[j])

        # print(self.matrix)


# Get TSP Solution using BnB
class TSP_solution:
    # Variables related to BnB
    def __init__(self, N, matrix, start, longest_time, solution_trace_files):
        self.final_path = []  # final paths
        self.visited = [False for i in range(N + 1)]  # visited lists to show whether city i is visited or not
        self.final_res = float('inf')  # final distance of the path
        self.size = N  # number of cities
        self.matrix = matrix  # matrix of cities
        self.sorted_indices = [[]]  # indices of closest neighbors for different cities
        self.start_time = start  # start time of the program
        self.longest_time = longest_time  # cutting_time
        self.trace_file = solution_trace_files  # solution_trace_file

    # Initialize TSP
    def TSP(self):
        # calculate indices of closest neighbors for different cities
        for i in range(1, self.size + 1):
            last_city_dist = self.matrix[i][1:]
            indices = np.argsort(last_city_dist)
            self.sorted_indices.append([i + 1 for i in indices])
        cur_path = [[]]
        cur_bound = 0
        # Lower Bound of the whole matrix of cities
        for i in range(1, self.size + 1):
            cur_bound += (min(self.matrix[i]) + second_smallest(self.matrix[i]))
        cur_bound = cur_bound / 2
        self.visited[1] = True
        cur_path.append(1)
        # Start TSP BnB
        self.TSP_BNB(cur_bound, 0, 1, cur_path)

    def TSP_BNB(self, cur_bound, cur_distance, level, cur_path):
        # When time is over cutting time, the program finished
        cur_time = time.time()
        if cur_time >= self.longest_time:
            return
        # When getting a solution
        if level == self.size:
            # calculate the sum of distance
            cur_res = cur_distance + self.matrix[cur_path[level]][cur_path[1]]
            # if the sum of distance is smaller than the previous best one, update it, and put it into trace_files
            if cur_res < self.final_res:
                self.final_path = cur_path[:]
                self.final_path.append(cur_path[1])
                self.final_res = cur_res
                print("%.2f" % round((cur_time - self.start_time), 2), self.final_res, sep=', ', file=self.trace_file)
                return

        # choose the closest city to the current one, then next
        last_city = cur_path[level]
        for i in self.sorted_indices[last_city]:
            if not self.visited[i]:
                prev_bound = cur_bound
                cur_distance += self.matrix[cur_path[level]][i]
                # update lower bound for current paths
                if level == 1:
                    cur_bound -= ((self.matrix[cur_path[level]][self.sorted_indices[cur_path[level]][0]] +
                                   self.matrix[i][self.sorted_indices[i][0]]) / 2)
                else:
                    cur_bound -= ((self.matrix[cur_path[level]][self.sorted_indices[cur_path[level]][1]] +
                                   self.matrix[i][self.sorted_indices[i][0]]) / 2)
                if cur_bound + cur_distance < self.final_res:
                    cur_path.append(i)
                    self.visited[i] = True
                    self.TSP_BNB(cur_bound, cur_distance, level + 1, cur_path)
                    self.visited[i] = False
                    cur_path.pop()
                # else we do pruning when current lower bound is larger the than previous best result
                cur_distance -= self.matrix[cur_path[level]][i]
                cur_bound = prev_bound
        return


# Main function for BnB
def runBranchAndBound(filename, cutoff_time):
    # read TSP files
    tspRead = TSP_Read()
    tspRead.read_file(filename)
    base = os.path.basename(filename)
    # cutting_time
    longest_interval = float(cutoff_time)
    # trace files
    solution_trace_file_name = base[:-4] + "_BnB" + "_" + cutoff_time + ".trace"
    solution_trace_files = open("./output/" + solution_trace_file_name, 'a+')
    # start BnB
    start = time.time()
    TSP = TSP_solution(tspRead.number, tspRead.matrix, start, longest_interval + start, solution_trace_files)
    TSP.TSP()
    # solution file
    solution_file_name = base[:-4] + "_BnB" + "_" + cutoff_time + ".sol"
    Solution_files = open("./output/" + solution_file_name, 'w+')
    print(TSP.final_res, ",".join(str(i) for i in [i-1 for i in TSP.final_path[1:-1]]), sep='\n', file=Solution_files)
