import sys
import BNB
import approx
import hillClimbing
import simanneal
import os

"""
This is the main program combining all algorithms together.
To run this program, use command:
tsp_main[.py] -inst <filename>
              -alg [BnB | Approx | LS1 | LS2]
              -time <cutoff_in_seconds> 
              [-seed <random_seed>]
"""

def main(args):

    # Catch error when there's not enough arguments
    if len(args) < 6:
        print("Usage: tsp_main[.py] -inst <filename> -alg [BnB | Approx | LS1 | LS2] -time <cutoff_in_seconds> [-seed <random_seed>]")
        return 1

    # Read arguments
    for i in range(0, len(args), 2):
        if args[i] == "-inst":
            file_name = args[i+1]
        if args[i] == "-alg":
            method = args[i+1]
        if args[i] == "-time":
            cutoff = args[i+1]
        if args[i] == "-seed":
            random_seed = args[i+1]

    path = os.getcwd() + "/output"
    folder = os.path.exists(path)

    if not folder:
        os.makedirs(path)

    # Run corresponding algorithm
    if method == 'BnB':
        BNB.runBranchAndBound(file_name, cutoff)
    if method == 'Approx':
        approx.mst_approx(file_name, cutoff, random_seed)
    if method == 'LS1':
        hillClimbing.runHillClimbing(file_name, cutoff, random_seed)
    if method == 'LS2':
        simanneal.runAnneal(file_name, cutoff, random_seed)

if __name__ == '__main__':
    main(sys.argv[1:])


