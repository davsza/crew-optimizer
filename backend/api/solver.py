from ortools.linear_solver import pywraplp
from .utils.agent_functions import get_current_week, get_roster_by_week
from .models import Roster
from django.contrib.auth.models import User


solver = pywraplp.Solver.CreateSolver('SCIP')


def solve():

    DAY_INDEX_START, DAY_INDEX_END = 1, 8
    ROSTER_INDEX_START, ROSTRE_INDEX_END = 22, 43

    def get_roster_mapping(rosters, start, end, offset=0):
        return {i - offset: rosters[i - start] for i in range(start, end)}

    def get_day_mapping(days, start, end):
        return {i: days[i - start] for i in range(start, end)}

    last_week_number = get_current_week(1)
    current_week_number = get_current_week(2)
    last_week_rosters = get_roster_by_week(last_week_number)
    current_week_rosters = get_roster_by_week(current_week_number)
    last_week_schedules = {}
    current_week_applications = {}
    last_week_work_days = {}
    last_week_off_days = {}
    last_week_reserve_days = {}

    # Sets
    WORKERS = []
    ROSTER_INDEX_1_42 = range(1, 43)  # 1-42
    ROSTER_INDEX_1_21 = range(1, 22)  # 1-21
    ROSTER_INDEX_22_42 = range(22, 43)  # 22-42
    DAYS_INDEX_1_7 = range(1, 8)  # 1-7
    DAYS_INDEX_1_8 = range(1, 9)  # 1-8
    DAYS_INDEX_1_13 = range(1, 14)  # 1-13
    DAYS_INDEX_1_14 = range(1, 15)  # 1-14
    DAYS_INDEX_8_13 = range(8, 14)  # 8-13
    DAYS_INDEX_8_14 = range(8, 15)  # 8-14
    DAYS_INDEX_9_14 = range(9, 15)  # 9-14

    for last_week_roster, current_week_roster in zip(last_week_rosters, current_week_rosters):
        username = current_week_roster.owner.username
        WORKERS.append(username)

        current_week_applications[username] = get_roster_mapping(
            current_week_roster.application, ROSTER_INDEX_START, ROSTRE_INDEX_END)
        last_week_schedules[username] = get_roster_mapping(
            last_week_roster.schedule, ROSTER_INDEX_START, ROSTRE_INDEX_END, ROSTER_INDEX_START - 1)
        last_week_work_days[username] = get_day_mapping(
            last_week_roster.work_days, DAY_INDEX_START, DAY_INDEX_END)
        last_week_off_days[username] = get_day_mapping(
            last_week_roster.off_days, DAY_INDEX_START, DAY_INDEX_END)
        last_week_reserve_days[username] = get_day_mapping(
            last_week_roster.reserve_days, DAY_INDEX_START, DAY_INDEX_END)

    # Parameters
    # TODO: parameter
    min_workers = {
        22: 2, 23: 4, 24: 2, 25: 2, 26: 4, 27: 2, 28: 2, 29: 4, 30: 2, 31: 2,
        32: 4, 33: 2, 34: 2, 35: 4, 36: 2, 37: 1, 38: 2, 39: 1, 40: 1, 41: 2, 42: 1
    }

    # Variables
    schedule = {}
    reserve = {}
    workDays = {}
    offDays = {}

    for w in WORKERS:
        for s in ROSTER_INDEX_1_42:
            schedule[w, s] = solver.BoolVar(f'schedule[{w},{s}]')

        for d in DAYS_INDEX_1_14:
            reserve[w, d] = solver.BoolVar(f'reserve[{w},{d}]')
            workDays[w, d] = solver.BoolVar(f'workDays[{w},{d}]')
            offDays[w, d] = solver.BoolVar(f'offDays[{w},{d}]')

    # Fix variables for the first week
    for w in WORKERS:
        for s in ROSTER_INDEX_1_21:
            schedule[w, s].SetBounds(
                int(last_week_schedules[w][s]), int(last_week_schedules[w][s]))
        for d in DAYS_INDEX_1_7:
            workDays[w, d].SetBounds(
                int(last_week_work_days[w][d]), int(last_week_work_days[w][d]))
            offDays[w, d].SetBounds(
                int(last_week_off_days[w][d]), int(last_week_off_days[w][d]))
            reserve[w, d].SetBounds(
                int(last_week_reserve_days[w][d]), int(last_week_reserve_days[w][d]))

    # Objective function: maximize the applications for the second week
    objective = solver.Objective()
    for w in WORKERS:
        for s in ROSTER_INDEX_22_42:
            coefficient = float(current_week_applications[w][s])
            objective.SetCoefficient(schedule[w, s], coefficient)

    objective.SetMaximization()

    # Constraints

    for w in WORKERS:

        # Each worker must work exactly 4 days (excluding reserve days) in the second week
        solver.Add(sum(schedule[w, s] for s in ROSTER_INDEX_22_42) == 4)

        # Each worker can work at most one shift per day in the second week
        for d in DAYS_INDEX_8_14:
            solver.Add(sum(schedule[w, (d - 1) * 3 + k]
                       for k in range(1, 4)) <= 1)

        # After night shifts, workers can't have morning or afternoon shift in both weeks
        # TODO: only for second week
        # for n in DAYS_INDEX_1_13:
        for n in DAYS_INDEX_8_13:
            solver.Add(sum(schedule[w, 3 + (n - 1) * 3 + k]
                       for k in range(3)) <= 1)

        # Each worker must have exactly one reserve day in the second week
        solver.Add(sum(reserve[w, d] for d in DAYS_INDEX_8_14) == 1)

        # No shifts on reserve days for each worker in the second week
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

    # Minimum required workers for each shift in the second week
    for s in ROSTER_INDEX_22_42:
        solver.Add(sum(schedule[w, s] for w in WORKERS) >= min_workers[s])

    # Each day must have at least 2 reserve workers in the second week
    for d in DAYS_INDEX_8_14:
        solver.Add(sum(reserve[w, d] for w in WORKERS) >= 2)

    # TODO: there has to be a 2 long day off in a 2 week period (sum off[i] * off[i + 1] >= 1)

    # Solve the model
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        for w, user_id in zip(WORKERS, range(7, 22)):
            roster_to_save = ""
            for s in ROSTER_INDEX_1_42:
                if s > 21:
                    roster_to_save += str(
                        int(schedule[w, s].solution_value()))

            user = User.objects.filter(id=user_id).first()
            roster = Roster.objects.filter(
                week_number=current_week_number, owner=user).first()
            roster.schedule = roster_to_save
            roster.save()
        for w, user_id in zip(WORKERS, range(7, 22)):
            work_days_str = ""
            off_days_str = ""
            reserve_days_str = ""
            for d in DAYS_INDEX_1_14:
                if d > 7:
                    work_days_str += str(int(workDays[w, d].solution_value()))
                    off_days_str += str(int(offDays[w, d].solution_value()))
                    reserve_days_str += str(
                        int(reserve[w, d].solution_value()))
            user = User.objects.filter(id=user_id).first()
            roster = Roster.objects.filter(
                week_number=current_week_number, owner=user).first()
            roster.work_days = work_days_str
            roster.off_days = off_days_str
            roster.reserve_days = reserve_days_str
            roster.save()
        print('Solution found')
    elif status == pywraplp.Solver.FEASIBLE:
        print('Feasible solution found but not optimal.')
    elif status == pywraplp.Solver.INFEASIBLE:
        print('The problem is infeasible.')
    elif status == pywraplp.Solver.UNBOUNDED:
        print('The problem is unbounded.')
    elif status == pywraplp.Solver.NOT_SOLVED:
        print('The problem was not solved.')
