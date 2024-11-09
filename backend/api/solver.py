from django.contrib.auth.models import User
from ortools.linear_solver import pywraplp
from .models import Roster
from .utils.agent_functions import (
    get_current_week,
    get_day_mapping,
    get_roster_mapping,
    get_rosters_by_week,
    max_consecutive_days,
)
from .utils.constants import CHAR_ZERO
from .utils.solver_constants import (
    DAYS_INDEX_1_13,
    DAYS_INDEX_1_14,
    DAYS_INDEX_1_7,
    DAYS_INDEX_1_8,
    DAYS_INDEX_8_13,
    DAYS_INDEX_8_14,
    DAYS_INDEX_9_14,
    DAY_INDEX_END,
    DAY_INDEX_START,
    ROSTER_INDEX_1_21,
    ROSTER_INDEX_1_42,
    ROSTER_INDEX_22_42,
    ROSTER_INDEX_START,
    ROSTRE_INDEX_END,
)


def optimize_schedule(number_of_users_to_solve, multiplier):

    solver = pywraplp.Solver.CreateSolver('SCIP')
    solver.SetSolverSpecificParametersAsString('display/verblevel=3')

    last_week_number = get_current_week(1)
    current_week_number = get_current_week(2)
    last_week_rosters = get_rosters_by_week(
        last_week_number, number_of_users_to_solve)
    current_week_rosters = get_rosters_by_week(
        current_week_number, number_of_users_to_solve)
    last_week_schedules = {}
    current_week_applications = {}
    last_week_work_days = {}
    last_week_off_days = {}
    last_week_reserve_days = {}
    current_week_vacation = {}

    # Sets
    WORKERS = []

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
        current_week_vacation[username] = get_day_mapping(
            current_week_roster.vacation, DAY_INDEX_START, DAY_INDEX_END)

    # Parameters
    min_workers = {
        22: 2, 23: 4, 24: 2, 25: 2, 26: 4, 27: 2, 28: 2, 29: 4, 30: 2, 31: 2,
        32: 4, 33: 2, 34: 2, 35: 4, 36: 2, 37: 1, 38: 2, 39: 1, 40: 1, 41: 2, 42: 1
    }

    min_workers = {key: value * multiplier for key,
                   value in min_workers.items()}

    # Variables
    schedule = {}
    reserve = {}
    workDays = {}
    offDays = {}
    vacation = {}

    for w in WORKERS:
        for s in ROSTER_INDEX_1_42:
            schedule[w, s] = solver.BoolVar(f'schedule[{w},{s}]')

        for d in DAYS_INDEX_1_14:
            reserve[w, d] = solver.BoolVar(f'reserve[{w},{d}]')
            workDays[w, d] = solver.BoolVar(f'workDays[{w},{d}]')
            offDays[w, d] = solver.BoolVar(f'offDays[{w},{d}]')
            vacation[w, d] = solver.BoolVar(f'vacation[{w},{d}]')

    for w in WORKERS:
        # Fix variables for the first week
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

        # Fix variables for the second week
        for d in DAYS_INDEX_8_14:
            if int(current_week_vacation[w][d - 7]) == 1:
                workDays[w, d].SetBounds(0, 0)
                offDays[w, d].SetBounds(0, 0)
                reserve[w, d].SetBounds(0, 0)
                vacation[w, d].SetBounds(1, 1)
            else:
                vacation[w, d].SetBounds(0, 0)

    # Objective function: maximize the applications for the second week
    # TODO: add min worker for each day
    objective = solver.Objective()
    for w in WORKERS:
        for s in ROSTER_INDEX_22_42:
            coefficient = float(current_week_applications[w][s])
            objective.SetCoefficient(schedule[w, s], coefficient)

    objective.SetMaximization()

    constraints = 0
    total_constraints = 0

    # Constraints
    for w in WORKERS:
        vacation_for_week = sum(int(vac)
                                for vac in current_week_vacation[w].values())
        vacation_binary = ''.join(current_week_vacation[w].values())
        max_consecutive_no_vac_days = max_consecutive_days(
            vacation_binary, CHAR_ZERO)
        number_of_work_days = min(4, 7 - vacation_for_week)
        number_of_off_days = max(2 - vacation_for_week, 0)
        number_of_reserve_days = 1 if vacation_for_week < 3 else 0

        # Define work days
        solver.Add(sum(workDays[w, d]
                   for d in DAYS_INDEX_8_14) == number_of_work_days)
        constraints += 1

        # Define off days
        solver.Add(sum(offDays[w, d]
                   for d in DAYS_INDEX_8_14) == number_of_off_days)
        constraints += 1

        # Define reserve days
        solver.Add(sum(reserve[w, d]
                   for d in DAYS_INDEX_8_14) == number_of_reserve_days)
        constraints += 1

        # Each day will be a working, off, reserve or a vacation day
        for d in DAYS_INDEX_8_14:
            solver.Add(workDays[w, d] + offDays[w, d] +
                       reserve[w, d] + vacation[w, d] == 1)
            constraints += 1

        # Each worker can only have shifts on workdays in the second week
        for d in DAYS_INDEX_8_14:
            solver.Add(sum(schedule[w, (d - 1) * 3 + k]
                       for k in range(1, 4)) == workDays[w, d])
            constraints += 1

        # Each worker can work at most one shift per day in the second week
        for d in DAYS_INDEX_8_14:
            solver.Add(sum(schedule[w, (d - 1) * 3 + k]
                       for k in range(1, 4)) <= 1)
            constraints += 1

        if number_of_off_days > 0 and max_consecutive_no_vac_days > 1:
            # Ensure a reserve day follows a day off
            for d in DAYS_INDEX_8_13:
                solver.Add(offDays[w, d + 1] >= reserve[w, d])
                constraints += 1

            # Ensure a reserve day cannot be preceded by an off day
            for d in DAYS_INDEX_9_14:
                solver.Add(offDays[w, d - 1] <= 1 - reserve[w, d])
                constraints += 1

        # After night shifts, workers can't have morning or afternoon shift in both weeks
        # TODO: only for second week
        for n in DAYS_INDEX_8_13:  # for n in DAYS_INDEX_1_13:
            solver.Add(sum(schedule[w, 3 + (n - 1) * 3 + k]
                       for k in range(3)) <= 1)
            constraints += 1

        total_constraints += constraints
        print(
            f'number of constraints for {w}: {constraints}. total: {total_constraints}')
        constraints = 0

    # Minimum required workers for each shift in the second week
    for s in ROSTER_INDEX_22_42:
        solver.Add(sum(schedule[w, s] for w in WORKERS) >= min_workers[s])
        total_constraints += 1

    # Each day must have at least 2 reserve workers in the second week
    for d in DAYS_INDEX_8_14:
        solver.Add(sum(reserve[w, d] for w in WORKERS) >= 2 * multiplier)
        total_constraints += 1

    # Solve the model
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        for w in WORKERS:
            schedule_str = ""
            work_days_str = ""
            off_days_str = ""
            reserve_days_str = ""

            user = User.objects.get(username=w)
            roster = Roster.objects.filter(
                week_number=current_week_number, owner=user).first()

            for s in ROSTER_INDEX_22_42:
                schedule_str += str(
                    int(schedule[w, s].solution_value()))
            roster.schedule = schedule_str

            for d in DAYS_INDEX_8_14:
                work_days_str += str(int(workDays[w, d].solution_value()))
                off_days_str += str(int(offDays[w, d].solution_value()))
                reserve_days_str += str(int(reserve[w, d].solution_value()))

            roster.work_days = work_days_str
            roster.off_days = off_days_str
            roster.reserve_days = reserve_days_str

            print(f'{user.username}\'s schedule: {schedule_str} - work days: {work_days_str}, off days: {off_days_str}, reserve days: {reserve_days_str}')

            roster.published = True
            roster.save()

        # Retrieve and print statistics
        print('Solver runtime (ms):', solver.WallTime())
        print('Number of constraints:', solver.NumConstraints())

    return status, constraints, solver.WallTime(), solver.NumConstraints()
