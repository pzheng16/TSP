from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import abc
import copy
import datetime
import math
import pickle
import random
import signal
import sys
import time

"""
TSP Simulated Annealing algorithm
"""


def round_figures(x, n):
    """Returns x rounded to n significant figures."""
    return round(x, int(n - math.ceil(math.log10(abs(x)))))


def time_string(seconds):
    """Returns time in seconds as a string formatted HHHH:MM:SS."""
    s = int(round(seconds))  # round to nearest second
    h, s = divmod(s, 3600)   # get hours and remainder
    m, s = divmod(s, 60)     # split remainder into minutes and seconds
    return '%4i:%02i:%02i' % (h, m, s)


class Annealer(object):

    """Performs simulated annealing by calling functions to calculate
    energy and make moves on a state.  The temperature schedule for
    annealing may be provided manually or estimated automatically.
    """

    __metaclass__ = abc.ABCMeta

    # defaults
    Tmax = 250000.0
    Tmin = 0.25
    steps = 500000
    updates = 100
    copy_strategy = 'deepcopy'
    user_exit = False
    save_state_on_exit = False

    # placeholders
    best_state = None
    best_energy = None
    start = None

    def __init__(self, initial_state=None, load_state=None):
        if initial_state is not None:
            self.state = self.copy_state(initial_state)
        elif load_state:
            self.load_state(load_state)
        else:
            raise ValueError('No valid values supplied for neither \
            initial_state nor load_state')

        signal.signal(signal.SIGINT, self.set_user_exit)

    def save_state(self, fname=None):
        """Saves state to pickle"""
        if not fname:
            date = datetime.datetime.now().strftime("%Y-%m-%dT%Hh%Mm%Ss")
            fname = date + "_energy_" + str(self.energy()) + ".state"
        with open(fname, "wb") as fh:
            pickle.dump(self.state, fh)

    def load_state(self, fname=None):
        """Loads state from pickle"""
        with open(fname, 'rb') as fh:
            self.state = pickle.load(fh)

    @abc.abstractmethod
    def move(self):
        """Create a state change"""
        pass

    @abc.abstractmethod
    def energy(self):
        """Calculate state's energy"""
        pass
    def set_user_exit(self, signum, frame):
        """Raises the user_exit flag, further iterations are stopped
        """
        self.user_exit = True
    def set_schedule(self, schedule):
        """Takes the output from `auto` and sets the attributes
        """
        self.Tmax = schedule['tmax']
        self.Tmin = schedule['tmin']
        self.steps = int(schedule['steps'])
        self.updates = int(schedule['updates'])

    def copy_state(self, state):
        """Returns an exact copy of the provided state
        Implemented according to self.copy_strategy, one of
        * deepcopy : use copy.deepcopy (slow but reliable)
        * slice: use list slices (faster but only works if state is list-like)
        * method: use the state's copy() method
        """
        if self.copy_strategy == 'deepcopy':
            return copy.deepcopy(state)
        elif self.copy_strategy == 'slice':
            return state[:]
        elif self.copy_strategy == 'method':
            return state.copy()
        else:
            raise RuntimeError('No implementation found for ' +
                               'the self.copy_strategy "%s"' %
                               self.copy_strategy)

    def anneal(self, cutoff_time, handle):
        """Minimizes the energy of a system by simulated annealing.
        Parameters
        state : an initial arrangement of the system
        Returns
        (state, energy): the best state and energy found.
        """
        step = 0
        self.start = time.time()

        # Precompute factor for exponential cooling from Tmax to Tmin
        if self.Tmin <= 0.0:
            raise Exception('Exponential cooling requires a minimum "\
                "temperature greater than zero.')
        Tfactor = -math.log(self.Tmax / self.Tmin)

        # Note initial state
        T = self.Tmax
        E = self.energy()
        prevState = self.copy_state(self.state)
        prevEnergy = E
        self.best_state = self.copy_state(self.state) # Initialize best state as initial state
        self.best_energy = E
        trials, accepts, improves = 0, 0, 0
        if self.updates > 0:
            updateWavelength = self.steps / self.updates

        # Attempt moves to new states
        while time.time() - self.start < cutoff_time:
            step += 1
            T = self.Tmax * math.exp(Tfactor * step / self.steps)
            dE = self.move()
            if dE is None:
                E = self.energy()
                dE = E - prevEnergy
            else:
                E += dE
            trials += 1

            if dE > 0.0 and math.exp(-dE / T) < random.random():
                # Restore previous state
                self.state = self.copy_state(prevState)
                E = prevEnergy
            else:
                # Accept new state and compare to best state
                accepts += 1
                if dE < 0.0:
                    improves += 1
                prevState = self.copy_state(self.state)
                prevEnergy = E
                if E < self.best_energy:
                    t = time.time() - self.start
                    handle.write("%.2f" % t + "\t" + str(int(E)) + "\n")
                    self.best_state = self.copy_state(self.state)
                    self.best_energy = E
            
            if self.updates > 1:
                if (step // updateWavelength) > ((step - 1) // updateWavelength):
                    trials, accepts, improves = 0, 0, 0

        self.state = self.copy_state(self.best_state)
        if self.save_state_on_exit:
            self.save_state()

        # Return best state and energy
        """
        print("elapsed: ", time.time() - self.start)
        print("-------end of anneal function-------")
        """
        return self.best_state, self.best_energy


class TravellingSalesmanProblem(Annealer):

    """Test annealer with a travelling salesman problem.
    """

    # pass extra data (the distance matrix) into the constructor
    def __init__(self, state, distance_matrix):
        self.distance_matrix = distance_matrix
        super(TravellingSalesmanProblem, self).__init__(state)  # important!

    def move(self):
        """Swaps two cities in the route."""
        initial_energy = self.energy()

        a = random.randint(0, len(self.state) - 1)
        b = random.randint(0, len(self.state) - 1)
                 
        self.state[a], self.state[b] = self.state[b], self.state[a]

        return self.energy() - initial_energy

    def energy(self):
        """Calculates the length of the route."""
        e = 0
        for i in range(len(self.state)):
            e += self.distance_matrix[self.state[i-1]][self.state[i]]
        return e

def read(path, nodes):
    f = open(path, 'r')
    for line in f.readlines():
        line = line.strip()
        if not len(line) or line.startswith('#'):
            continue
        if not line[0].isnumeric():
            continue
        node_id, x, y = line.split()
        nodes[node_id] = (float(x), float(y))
    f.close()

def distance(a, b):
    """Calculates distance between two latitude-longitude coordinates."""
    x1, y1 = a[0], a[1]
    x2, y2 = b[0], b[1]
    return round(math.sqrt((x1-x2)**2 + (y1-y2)**2))

def runAnneal(path, cutoff_time, random_seed):
    cutoff_time = float(cutoff_time)
    random_seed = float(random_seed)
    results = {}
    nodes = {}
    # read file into nodes
    read(path, nodes)
    
    distance_matrix = {}
    # create a distance matrix
    for ka, va in nodes.items():
        distance_matrix[ka] = {}
        for kb, vb in nodes.items():
            if kb == ka:
                distance_matrix[ka][kb] = 0.0
            else:
                distance_matrix[ka][kb] = distance(va, vb)    

    filename = path.split("/")[-1]
    city = filename.split(".")[0]
    outputFile = city + "_LS2_" + str(cutoff_time) + "_" + str(random_seed) + ".sol"
    traceFile = city + "_LS2_" + str(cutoff_time) + "_" + str(random_seed) + ".trace"
    f_out = open("./output/" + outputFile, "w+")
    f_trace = open("./output/" + traceFile, "w+")

    random.seed(random_seed)
    init_state = list(nodes.keys())
    # initial state, a randomly-ordered itinerary
    random.shuffle(init_state)
    
    tsp = TravellingSalesmanProblem(init_state, distance_matrix)
    tsp.copy_strategy = "slice"     # since our state is just a list, slice is the fastest way to copy
    state, e = tsp.anneal(cutoff_time, f_trace)

    while state[0] != '1':
        state = state[1:] + state[:1]  # rotate node 1 to start
    for i in range(len(state)):
        state[i] = str(int(state[i]) - 1)

    route = ",".join(state)
    """print(city + ": " + str(int(e)) + " miles. Route: " + route)"""
    f_out.write(str(int(e)) + "\n" + route + "\n")


    f_out.close()
    f_trace.close()

