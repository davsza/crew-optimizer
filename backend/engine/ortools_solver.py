from ortools.linear_solver import pywraplp


def nl():
    print()


def main():
    # Define the sets
    # Will have to change it
    workers = ['W1', 'W2', 'W3', 'W4', 'W5', 'W6', 'W7',
               'W8', 'W9', 'W10', 'W11', 'W12', 'W13', 'W14', 'W15']
    shifts = list(range(1, 22))
    days = list(range(1, 8))
    nights = list(range(1, 7))

    # Define the parameters
    # Will have to change it
    min_workers = {
        1: 2, 2: 4, 3: 2, 4: 2, 5: 4, 6: 2, 7: 2, 8: 4, 9: 2, 10: 2, 11: 4,
        12: 2, 13: 2, 14: 4, 15: 2, 16: 1, 17: 2, 18: 1, 19: 1, 20: 2, 21: 1
    }

    # Will have to change it
    application = {
        'W1': [1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1, 0],
        'W2': [0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1],
        'W3': [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1],
        'W4': [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1],
        'W5': [0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0],
        'W6': [1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0],
        'W7': [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 1, 0, 1],
        'W8': [1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0],
        'W9': [1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0],
        'W10': [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0],
        'W11': [0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1],
        'W12': [0, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        'W13': [1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1],
        'W14': [0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 1, 0, 1],
        'W15': [1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1]
    }

    # Create the solver with the SCIP backend
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        print('SCIP solver unavailable.')
        return

    # Create the variables
    # var x{WORKERS, SHIFTS} binary;  # Binary variable indicating worker assignment
    x = {}
    for i in workers:
        for j in shifts:
            x[i, j] = solver.BoolVar(f'x[{i},{j}]')

    # var res{WORKERS, DAYS} binary;  # Binary variable indicating reserve day
    res = {}
    for i in workers:
        for j in shifts:
            res[i, j] = solver.BoolVar(f'res[{i},{j}]')

    # Objective function: maximize the total match
    # maximize Total_Match:
    #   sum {i in WORKERS, j in SHIFTS} x[i, j] * application[i, j];
    objective = solver.Objective()
    for i in workers:
        for j in shifts:
            objective.SetCoefficient(x[i, j], application[i][j-1])
    objective.SetMaximization()

    # Constraint: each worker must work exactly 5 days (excluding reserve days)
    # subject to Work_Constraint {i in WORKERS}:
    #   sum {j in SHIFTS} x[i,j] = 5;
    for i in workers:
        solver.Add(sum(x[i, j] for j in shifts) == 5)

    # Constraint: each worker can work at most one shift per day
    # subject to Max_One_Shift_Per_Day {i in WORKERS, j in DAYS}:
    #   sum {k in 1..3} x[i, (j - 1) * 3 + k] <= 1;
    for i in workers:
        for j in days:
            solver.Add(sum(x[i, (j - 1) * 3 + k] for k in range(1, 4)) <= 1)

    # Constraint: workers can't have any morning or afternoon shift after night shifts
    # subject to Night_Shifts {i in WORKERS, j in NIGHTS}:
    #   sum {k in 0..2} x[i, 3 + (j - 1) * 3 + k] <= 1;
    for i in workers:
        for j in nights:
            solver.Add(sum(x[i, 3 + (j - 1) * 3 + k] for k in range(3)) <= 1)

    # Constraint: minimum required workers for each shift
    # subject to Min_Workers_Constraint {j in SHIFTS}:
    #   sum {i in WORKERS} x[i,j] >= min_workers[j];
    for j in shifts:
        solver.Add(sum(x[i, j] for i in workers) >= min_workers[j])

    # Constraint: minimum required reserves for each day
    # subject to Min_Reserve_Workers_Per_Day {j in DAYS}:
    #   sum {i in WORKERS} res[i, j] >= 2;
    for j in days:
        solver.Add(sum(res[i, j] for i in workers) >= 2)

    # Constraint: each worker must have exactly one reserve day
    # subject to Reserve_Constraint {i in WORKERS}:
    #   sum {j in DAYS} res[i, j] = 1;
    for i in workers:
        solver.Add(sum(res[i, j] for j in days) == 1)

    # Constraint: no shifts on reserve day for each worker
    # subject to No_Shift_On_Reserve_Day {i in WORKERS, j in DAYS}:
    #   sum {k in 1..3} x[i, (j - 1) * 3 + k] <= (1 - res[i, j]) * 3;
    for i in workers:
        for j in days:
            solver.Add(sum(x[i, (j - 1) * 3 + k]
                       for k in range(1, 4)) <= (1 - res[i, j]))

    # Solve the problem
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        print("Solution:")
        for i in workers:
            # print(f"Worker {i} is assigned to shifts:", end=" ")
            print(f"{i}:", end=" ")
            for j in shifts:
                # if x[i, j].solution_value() == 1:
                #     print(j, end=" ")
                print(int(x[i, j].solution_value()), ' ', end=" ")
            nl()
        for i in workers:
            print(f"{i}:", end=" ")
            for j in days:
                print(int(res[i, j].solution_value()), ' ', end=" ")
            nl()
        print(f"Total match value = {solver.Objective().Value()}")
        print(f"Objective value (Total match value) = {solver.Objective().Value()}")
    else:
        print("No optimal solution found!")

    # Statistics
    print("\nStatistics")
    print(f"  - wall time: {solver.WallTime()}s")


if __name__ == "__main__":
    main()
