from ortools.linear_solver import pywraplp
import random

# Create the solver
solver = pywraplp.Solver.CreateSolver('SCIP')

# Sets
WORKERS = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7',
           'W8', 'W9', 'W10', 'W11', 'W12', 'W13', 'W14', 'W15']
SHIFT_INDEX_1_42 = range(1, 43)  # 1-42
SHIFT_INDEX_1_21 = range(1, 22)  # 1-21
SHIFT_INDEX_22_42 = range(22, 43)  # 22-42
DAYS_INDEX_1_7 = range(1, 8)  # 1-7
DAYS_INDEX_1_8 = range(1, 9)  # 1-8
DAYS_INDEX_1_13 = range(1, 14)  # 1-13
DAYS_INDEX_1_14 = range(1, 15)  # 1-14
DAYS_INDEX_2_14 = range(2, 15)  # 2-14
DAYS_INDEX_8_13 = range(8, 14)  # 8-13
DAYS_INDEX_8_14 = range(8, 15)  # 8-14
DAYS_INDEX_9_14 = range(9, 15)  # 9-14


# Parameters
min_workers = {
    22: 2, 23: 4, 24: 2, 25: 2, 26: 4, 27: 2, 28: 2, 29: 4, 30: 2, 31: 2,
    32: 4, 33: 2, 34: 2, 35: 4, 36: 2, 37: 1, 38: 2, 39: 1, 40: 1, 41: 2, 42: 1
}

# param application :
# 	  22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 :=
# W1   1  0  1  1  0  1  0  0  0  0  0  1  0  0  0  0  1  0  1  1  0
# W2   0  1  1  0  1  1  1  1  0  0  0  0  0  1  0  0  0  1  0  1  1
# W3   0  0  0  0  0  0  1  1  1  1  1  1  1  1  1  1  0  1  1  0  1
# W4   1  0  1  1  0  1  0  1  1  1  0  0  1  0  0  1  1  0  1  1  1
# W5   0  1  1  1  1  1  1  0  1  0  0  1  0  1  1  0  1  1  0  1  0
# W6   1  1  1  1  1  1  1  0  1  0  1  1  1  1  1  0  1  0  1  1  0
# W7   0  0  1  0  0  0  0  1  0  0  1  0  0  1  1  1  1  1  1  0  1
# W8   1  0  1  1  0  1  0  0  0  0  1  1  0  1  0  1  1  1  1  1  0
# W9   1  0  0  1  1  0  1  0  1  1  1  0  0  1  1  0  1  1  0  1  0
# W10  1  0  1  1  0  1  1  1  0  1  1  1  0  0  1  0  0  0  1  1  0
# W11  0  0  1  0  0  1  1  0  1  1  1  0  0  0  1  1  1  0  1  1  1
# W12  0  0  0  1  1  0  0  0  1  1  1  0  0  0  0  0  0  0  1  0  0
# W13  1  0  1  1  0  0  1  0  0  0  1  1  0  0  1  1  1  0  1  1  1
# W14  0  1  0  1  1  0  0  0  1  1  1  1  1  1  0  0  0  1  1  0  1
# W15  1  1  0  1  1  1  0  1  1  0  1  1  1  0  0  0  0  1  0  0  1;

application = {
    'W1': {22: 1, 23: 0, 24: 1, 25: 1, 26: 0, 27: 1, 28: 0, 29: 0, 30: 0, 31: 0, 32: 0, 33: 1, 34: 0, 35: 0, 36: 0, 37: 0, 38: 1, 39: 0, 40: 1, 41: 1, 42: 0},
    'W2': {22: 0, 23: 1, 24: 1, 25: 0, 26: 1, 27: 1, 28: 1, 29: 1, 30: 0, 31: 0, 32: 0, 33: 0, 34: 0, 35: 1, 36: 0, 37: 0, 38: 0, 39: 1, 40: 0, 41: 1, 42: 1},
    'W3': {22: 0, 23: 0, 24: 0, 25: 0, 26: 0, 27: 0, 28: 1, 29: 1, 30: 1, 31: 1, 32: 1, 33: 1, 34: 1, 35: 1, 36: 1, 37: 1, 38: 0, 39: 1, 40: 1, 41: 0, 42: 1},
    'W4': {22: 1, 23: 0, 24: 1, 25: 1, 26: 0, 27: 1, 28: 0, 29: 1, 30: 1, 31: 1, 32: 0, 33: 0, 34: 1, 35: 0, 36: 0, 37: 1, 38: 1, 39: 0, 40: 1, 41: 1, 42: 1},
    'W5': {22: 0, 23: 1, 24: 1, 25: 1, 26: 1, 27: 1, 28: 1, 29: 0, 30: 1, 31: 0, 32: 0, 33: 1, 34: 0, 35: 1, 36: 1, 37: 0, 38: 1, 39: 1, 40: 0, 41: 1, 42: 0},
    'W6': {22: 1, 23: 1, 24: 1, 25: 1, 26: 1, 27: 1, 28: 1, 29: 0, 30: 1, 31: 0, 32: 1, 33: 1, 34: 1, 35: 1, 36: 1, 37: 0, 38: 1, 39: 0, 40: 1, 41: 1, 42: 0},
    'W7': {22: 0, 23: 0, 24: 1, 25: 0, 26: 0, 27: 0, 28: 0, 29: 1, 30: 0, 31: 0, 32: 1, 33: 0, 34: 0, 35: 1, 36: 1, 37: 1, 38: 1, 39: 1, 40: 0, 41: 1, 42: 1},
    'W8': {22: 1, 23: 0, 24: 1, 25: 1, 26: 0, 27: 1, 28: 0, 29: 0, 30: 0, 31: 0, 32: 1, 33: 1, 34: 0, 35: 1, 36: 0, 37: 1, 38: 1, 39: 1, 40: 1, 41: 1, 42: 0},
    'W9': {22: 1, 23: 0, 24: 0, 25: 1, 26: 1, 27: 0, 28: 1, 29: 0, 30: 1, 31: 1, 32: 1, 33: 0, 34: 0, 35: 1, 36: 1, 37: 0, 38: 1, 39: 1, 40: 0, 41: 1, 42: 0},
    'W10': {22: 1, 23: 0, 24: 1, 25: 1, 26: 0, 27: 1, 28: 1, 29: 1, 30: 0, 31: 1, 32: 1, 33: 1, 34: 0, 35: 0, 36: 1, 37: 0, 38: 0, 39: 0, 40: 1, 41: 1, 42: 0},
    'W11': {22: 0, 23: 0, 24: 1, 25: 0, 26: 0, 27: 1, 28: 1, 29: 0, 30: 1, 31: 1, 32: 1, 33: 0, 34: 0, 35: 0, 36: 1, 37: 1, 38: 1, 39: 0, 40: 1, 41: 1, 42: 1},
    'W12': {22: 0, 23: 0, 24: 0, 25: 1, 26: 1, 27: 0, 28: 0, 29: 0, 30: 1, 31: 1, 32: 1, 33: 0, 34: 0, 35: 0, 36: 0, 37: 0, 38: 0, 39: 0, 40: 1, 41: 0, 42: 0},
    'W13': {22: 1, 23: 0, 24: 1, 25: 1, 26: 0, 27: 0, 28: 1, 29: 0, 30: 0, 31: 0, 32: 1, 33: 1, 34: 0, 35: 0, 36: 1, 37: 1, 38: 1, 39: 0, 40: 1, 41: 1, 42: 1},
    'W14': {22: 0, 23: 1, 24: 0, 25: 1, 26: 1, 27: 0, 28: 0, 29: 0, 30: 1, 31: 1, 32: 1, 33: 1, 34: 1, 35: 1, 36: 0, 37: 0, 38: 0, 39: 1, 40: 1, 41: 0, 42: 1},
    'W15': {22: 1, 23: 1, 24: 0, 25: 1, 26: 1, 27: 1, 28: 0, 29: 1, 30: 1, 31: 0, 32: 1, 33: 1, 34: 1, 35: 0, 36: 0, 37: 0, 38: 1, 39: 0, 40: 0, 41: 1, 42: 1}
}

newApplication = {}
for w in WORKERS:
    w_application = {}
    for i in range(22, 43):
        w_application[i] = random.randint(0, 1)
    newApplication[w] = w_application
# print(newApplication)

# param fixShift :
#      1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 :=
# W1   0  0  0  0  0  1  0  0  0  0  0  1  0  0  0  0  1  0  1  0  0
# W2   0  1  0  0  1  0  0  1  0  0  0  0  0  0  0  0  0  1  0  0  0
# W3   0  0  0  0  0  0  0  1  0  0  0  1  0  0  0  1  0  0  0  0  1
# W4   0  0  0  1  0  0  0  1  0  1  0  0  1  0  0  0  0  0  0  0  0
# W5   0  0  0  0  1  0  0  0  1  0  0  0  0  0  0  0  1  0  0  1  0
# W6   0  1  0  0  1  0  0  0  0  0  0  0  0  1  0  0  0  0  0  1  0
# W7   0  0  0  0  0  0  0  1  0  0  0  0  0  0  1  0  0  1  0  0  1
# W8   1  0  0  0  0  0  0  0  0  0  1  0  0  1  0  0  0  0  0  1  0
# W9   0  0  0  1  0  0  1  0  0  0  0  0  0  1  0  0  1  0  0  0  0
# W10  1  0  0  0  0  0  0  0  0  1  0  0  0  0  1  0  0  0  0  1  0
# W11  0  0  1  0  0  0  1  0  0  0  1  0  0  0  0  0  1  0  0  0  0
# W12  0  0  0  0  1  0  0  0  1  0  0  0  0  0  0  1  0  0  1  0  0
# W13  0  0  1  0  0  0  0  0  0  0  1  0  0  0  0  0  1  0  0  1  0
# W14  0  1  0  0  0  0  0  0  0  0  1  0  0  1  0  0  0  1  0  0  0
# W15  0  1  0  0  0  1  0  0  0  0  1  0  1  0  0  0  0  0  0  0  0;

fixShift = {
    'W1': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 1, 13: 0, 14: 0, 15: 0, 16: 0, 17: 1, 18: 0, 19: 1, 20: 0, 21: 0},
    'W2': {1: 0, 2: 1, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0, 8: 1, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 1, 19: 0, 20: 0, 21: 0},
    'W3': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 1, 9: 0, 10: 0, 11: 0, 12: 1, 13: 0, 14: 0, 15: 0, 16: 1, 17: 0, 18: 0, 19: 0, 20: 0, 21: 1},
    'W4': {1: 0, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0, 7: 0, 8: 1, 9: 0, 10: 1, 11: 0, 12: 0, 13: 1, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0},
    'W5': {1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0, 8: 0, 9: 1, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 1, 18: 0, 19: 0, 20: 1, 21: 0},
    'W6': {1: 0, 2: 1, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 1, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 1, 21: 0},
    'W7': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 1, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 1, 16: 0, 17: 0, 18: 1, 19: 0, 20: 0, 21: 1},
    'W8': {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 1, 12: 0, 13: 0, 14: 1, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 1, 21: 0},
    'W9': {1: 0, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0, 7: 1, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 1, 15: 0, 16: 0, 17: 1, 18: 0, 19: 0, 20: 0, 21: 0},
    'W10': {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 1, 11: 0, 12: 0, 13: 0, 14: 0, 15: 1, 16: 0, 17: 0, 18: 0, 19: 0, 20: 1, 21: 0},
    'W11': {1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 0, 7: 1, 8: 0, 9: 0, 10: 0, 11: 1, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 1, 18: 0, 19: 0, 20: 0, 21: 0},
    'W12': {1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0, 8: 0, 9: 1, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 1, 17: 0, 18: 0, 19: 1, 20: 0, 21: 0},
    'W13': {1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 1, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 1, 18: 0, 19: 0, 20: 1, 21: 0},
    'W14': {1: 0, 2: 1, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0, 11: 1, 12: 0, 13: 0, 14: 1, 15: 0, 16: 0, 17: 0, 18: 1, 19: 0, 20: 0, 21: 0},
    'W15': {1: 0, 2: 1, 3: 0, 4: 0, 5: 0, 6: 1, 7: 0, 8: 0, 9: 0, 10: 0, 11: 1, 12: 0, 13: 1, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0, 21: 0}
}

# param fixReserve :
#       1   2   3   4   5   6   7    :=
# W1    1   0   0   0   0   0   0
# W2    0   0   0   0   0   0   1
# W3    0   1   0   0   0   0   0
# W4    0   0   0   0   0   1   0
# W5    0   0   0   1   0   0   0
# W6    0   0   0   0   0   1   0
# W7    1   0   0   0   0   0   0
# W8    0   1   0   0   0   0   0
# W9    0   0   0   0   0   0   1
# W10   0   0   0   0   0   1   0
# W11   0   0   0   0   1   0   0
# W12   0   0   0   1   0   0   0
# W13   0   0   0   0   1   0   0
# W14   0   0   1   0   0   0   0
# W15   0   0   1   0   0   0   0;

fixReserve = {
    'W1': {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
    'W2': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1},
    'W3': {1: 0, 2: 1, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
    'W4': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1, 7: 0},
    'W5': {1: 0, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0, 7: 0},
    'W6': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1, 7: 0},
    'W7': {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
    'W8': {1: 0, 2: 1, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0},
    'W9': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1},
    'W10': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1, 7: 0},
    'W11': {1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0},
    'W12': {1: 0, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0, 7: 0},
    'W13': {1: 0, 2: 0, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0},
    'W14': {1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0},
    'W15': {1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0}
}

# param fixWorkDays :
#       1   2   3   4   5   6   7    :=
# W1    0   1   0   1   0   1   1
# W2    1   1   1   0   0   1   0
# W3    0   0   1   1   0   1   1
# W4    0   1   1   1   1   0   0
# W5    0   1   1   0   0   1   1
# W6    1   1   0   0   1   0   1
# W7    0   0   1   0   1   1   1
# W8    1   0   0   1   1   0   1
# W9    0   1   1   0   1   1   0
# W10   1   0   0   1   1   0   1
# W11   1   0   1   1   0   1   0
# W12   0   1   1   0   0   1   1
# W13   1   0   0   1   0   1   1
# W14   1   0   0   1   1   1   0
# W15   1   1   0   1   1   0   0;

fixWorkDays = {
    'W1': {1: 0, 2: 1, 3: 0, 4: 1, 5: 0, 6: 1, 7: 1},
    'W2': {1: 1, 2: 1, 3: 1, 4: 0, 5: 0, 6: 1, 7: 0},
    'W3': {1: 0, 2: 0, 3: 1, 4: 1, 5: 0, 6: 1, 7: 1},
    'W4': {1: 0, 2: 1, 3: 1, 4: 1, 5: 1, 6: 0, 7: 0},
    'W5': {1: 0, 2: 1, 3: 1, 4: 0, 5: 0, 6: 1, 7: 1},
    'W6': {1: 1, 2: 1, 3: 0, 4: 0, 5: 1, 6: 0, 7: 1},
    'W7': {1: 0, 2: 0, 3: 1, 4: 0, 5: 1, 6: 1, 7: 1},
    'W8': {1: 1, 2: 0, 3: 0, 4: 1, 5: 1, 6: 0, 7: 1},
    'W9': {1: 0, 2: 1, 3: 1, 4: 0, 5: 1, 6: 1, 7: 0},
    'W10': {1: 1, 2: 0, 3: 0, 4: 1, 5: 1, 6: 0, 7: 1},
    'W11': {1: 1, 2: 0, 3: 1, 4: 1, 5: 0, 6: 1, 7: 0},
    'W12': {1: 0, 2: 1, 3: 1, 4: 0, 5: 0, 6: 1, 7: 1},
    'W13': {1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 1, 7: 1},
    'W14': {1: 1, 2: 0, 3: 0, 4: 1, 5: 1, 6: 1, 7: 0},
    'W15': {1: 1, 2: 1, 3: 0, 4: 1, 5: 1, 6: 0, 7: 0}
}

# param fixOffDays :
#       1   2   3   4   5   6   7    :=
# W1    0   0   1   0   1   0   0
# W2    0   0   0   1   1   0   0
# W3    1   0   0   0   1   0   0
# W4    1   0   0   0   0   0   1
# W5    1   0   0   0   1   0   0
# W6    0   0   1   1   0   0   0
# W7    0   1   0   1   0   0   0
# W8    0   0   1   0   0   1   0
# W9    1   0   0   1   0   0   0
# W10   0   1   1   0   0   0   0
# W11   0   1   0   0   0   0   1
# W12   1   0   0   0   1   0   0
# W13   0   1   1   0   0   0   0
# W14   0   1   0   0   0   0   1
# W15   0   0   0   0   0   1   1;

fixOffDays = {
    'W1': {1: 0, 2: 0, 3: 1, 4: 0, 5: 1, 6: 0, 7: 0},
    'W2': {1: 0, 2: 0, 3: 0, 4: 1, 5: 1, 6: 0, 7: 0},
    'W3': {1: 1, 2: 0, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0},
    'W4': {1: 1, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1},
    'W5': {1: 1, 2: 0, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0},
    'W6': {1: 0, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0, 7: 0},
    'W7': {1: 0, 2: 1, 3: 0, 4: 1, 5: 0, 6: 0, 7: 0},
    'W8': {1: 0, 2: 0, 3: 1, 4: 0, 5: 0, 6: 1, 7: 0},
    'W9': {1: 1, 2: 0, 3: 0, 4: 1, 5: 0, 6: 0, 7: 0},
    'W10': {1: 0, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0},
    'W11': {1: 0, 2: 1, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1},
    'W12': {1: 1, 2: 0, 3: 0, 4: 0, 5: 1, 6: 0, 7: 0},
    'W13': {1: 0, 2: 1, 3: 1, 4: 0, 5: 0, 6: 0, 7: 0},
    'W14': {1: 0, 2: 1, 3: 0, 4: 0, 5: 0, 6: 0, 7: 1},
    'W15': {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 1, 7: 1}
}


# Variables
schedule = {}
reserve = {}
workDays = {}
offDays = {}

for w in WORKERS:
    for s in SHIFT_INDEX_1_42:
        schedule[w, s] = solver.BoolVar(f'schedule[{w},{s}]')

    for d in DAYS_INDEX_1_14:
        reserve[w, d] = solver.BoolVar(f'reserve[{w},{d}]')
        workDays[w, d] = solver.BoolVar(f'workDays[{w},{d}]')
        offDays[w, d] = solver.BoolVar(f'offDays[{w},{d}]')

# Fix variables for the first week
for w in WORKERS:
    for s in SHIFT_INDEX_1_21:
        schedule[w, s].SetBounds(fixShift[w][s], fixShift[w][s])
    for d in DAYS_INDEX_1_7:
        reserve[w, d].SetBounds(fixReserve[w][d], fixReserve[w][d])
        workDays[w, d].SetBounds(fixWorkDays[w][d], fixWorkDays[w][d])
        offDays[w, d].SetBounds(fixOffDays[w][d], fixOffDays[w][d])

# Objective function: maximize the applications for the second week
objective = solver.Objective()
for w in WORKERS:
    for s in SHIFT_INDEX_22_42:
        objective.SetCoefficient(schedule[w, s], newApplication[w][s])
objective.SetMaximization()

# Constraints

for w in WORKERS:

    # Each worker must work exactly 4 days (excluding reserve days) in the second week
    solver.Add(sum(schedule[w, s] for s in SHIFT_INDEX_22_42) == 4)

    # Each worker can work at most one shift per day in the second week
    for d in DAYS_INDEX_8_14:
        solver.Add(sum(schedule[w, (d - 1) * 3 + k] for k in range(1, 4)) <= 1)

    # After night shifts, workers can't have morning or afternoon shift in both weeks
    for n in DAYS_INDEX_1_13:
        solver.Add(sum(schedule[w, 3 + (n - 1) * 3 + k]
                   for k in range(3)) <= 1)

    # Each worker must have exactly one reserve day in the second week
    solver.Add(sum(reserve[w, d] for d in DAYS_INDEX_8_14) == 1)

    # No shifts on reserve day for each worker in the second week
    for d in DAYS_INDEX_8_14:
        solver.Add(sum(schedule[w, (d - 1) * 3 + k]
                   for k in range(1, 4)) <= (1 - reserve[w, d]) * 3)

    # Define workDays based on schedule in the second week
    for d in DAYS_INDEX_8_14:
        solver.Add(workDays[w, d] == solver.Sum(
            [schedule[w, (d - 1) * 3 + k] for k in range(1, 4)]))

    # Define offDays based on workDays and reserve in the second week
    for d in DAYS_INDEX_8_14:
        solver.Add(offDays[w, d] == (1 - workDays[w, d] - reserve[w, d]))

    # Ensure at least one off day in every 7-day window
    for start_day in DAYS_INDEX_1_8:
        solver.Add(sum(workDays[w, d] for d in range(start_day, start_day + 7)) +
                   sum(reserve[w, d] for d in range(start_day, start_day + 7)) <= 6)

    # Ensure a reserve day follows a day off
    for d in DAYS_INDEX_8_13:
        solver.Add(offDays[w, d + 1] >= reserve[w, d])

    # Ensure a reserve day cannot be preceded by an off day
    for d in DAYS_INDEX_9_14:
        solver.Add(offDays[w, d - 1] <= 1 - reserve[w, d])
    
    # solver.Add(sum(offDays[w, d] + offDays[w, d + 1] for d in DAYS_INDEX_8_13) == 4)


# Minimum required workers for each shift in the second week
for s in SHIFT_INDEX_22_42:
    solver.Add(sum(schedule[w, s] for w in WORKERS) >= min_workers[s])


# Each day must have at least 2 reserve workers in the second week
for d in DAYS_INDEX_8_14:
    solver.Add(sum(reserve[w, d] for w in WORKERS) >= 2)


# TODO: there has to be a 2 long day off in a 2 week period (sum off[i] * off[i + 1] >= 1)


# Solve the model
status = solver.Solve()

days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def nl():
    print()


def space(times):
    print(' ' * times, end='')


if status == pywraplp.Solver.OPTIMAL:
    print("SHIFTS")
    space(7)
    for day in 2 * days:
        print(day, '   ', end='')
    nl()
    for w in WORKERS:
        print(f"{' ' if len(w) < 3 else ''}{w}: ", end=' ')
        for s in SHIFT_INDEX_1_42:
            print(int(schedule[w, s].solution_value()), end=' ')
            if s % 3 == 0:
                space(1)
        nl()
    nl()
    space(6)
    for day in 2 * days:
        print(day[0], end=' ')
        if day == "Sun":
            space(1)
    print()
    for w in WORKERS:
        print(f"{' ' if len(w) < 3 else ''}{w}: ", end=' ')
        for d in DAYS_INDEX_1_14:
            print('W' if int(workDays[w, d].solution_value()) == 1 else 'O' if int(
                offDays[w, d].solution_value()) == 1 else 'R', end=' ')
            if d == 7:
                space(1)
        nl()
else:
    print('No solution found.')
