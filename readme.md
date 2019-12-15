# TSP

The Traveling Salesman Problem (TSP) arises in numerous applications such as vehicle routing,
circuit board drilling, VLSI design, robot control, X-ray crystallography, machine scheduling and
computational biology. In this project, you will attempt to solve the TSP using different algorithms,
evaluating their theoretical and experimental complexities on both real and random datasets.

Our program aims at solving traveling salseman problem with four different algorithms. Five python source files are included in our final product, which are:

1. tsp_main.py: The user interface of our program
2. BnB.py: The branch and bound algorithm
3. approx.py: The MST-approximation algorithm
4. hillClimbing.py: The hill climbing algorithm
5. simanneal.py: The simulated annealing algorithm

To run our code, please use the command:

	python tsp_main.py -inst <filename> -alg [BnB | Approx | LS1 | LS2] -time <cutoff_in_seconds> [-seed <random_seed>]

All packages used are included in Anaconda 3 on PACE. If testing our codes on PACE, run

	module load anaconda3/latest

to get all packages needed for our codes. 

Our output files are in the output directory.
