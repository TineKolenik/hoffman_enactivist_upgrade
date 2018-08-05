import numpy as np
import itertools as it

# STATES
STATES = list(set(state for state in it.product([None, 0, 1, 2], repeat=5)
                  if state.count(None)==3))

# CONFIG
POPULATION = 200
GENERATIONS = 500
LIFESPAN = 50
TRIES = 100
MUTATION = 300
DNA_ACTION_LENGTH = len(STATES)
DNA_PERCEPTION_LENGTH = 11

# PERCEPTION STRATEGIES
REALIST = np.array([0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
CONSTRUCTIVIST = np.array([0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0])
ALTERNIST = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0])

# POINTS
PICKUP_POINTS = {0: 0,
                 1: 1,
                 2: 3,
                 3: 6,
                 4: 9,
                 5: 10,
                 6: 9,
                 7: 6,
                 8: 3,
                 9: 1,
                 10: 0}
PICKUP_PENALTY = 1
CRASH_PENALTY = 5
