from django.contrib.auth.models import User
from ortools.linear_solver import pywraplp

from .models import Roster
from .utils.common_fn import (
    get_day_mapping,
    get_roster_mapping,
    max_consecutive_days_in_roster,
)
from .utils.constants import CHAR_ZERO
from .utils.date_time_fn import get_current_week
from .utils.model_fn import get_rosters_by_week
from .utils.solver_constants import (
    DAYS_INDEX_1_13,
    DAYS_INDEX_1_14,
    DAYS_INDEX_1_7,
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


def add_worker_constraints_to_solver(solver, worker, workDays, offDays, reserve, vacation, sickness, schedule, current_week_vacation):
    vacation_for_week = sum(int(vac)
                            for vac in current_week_vacation[worker].values())
    vacation_binary = ''.join(current_week_vacation[worker].values())
    max_consecutive_no_vac_days = max_consecutive_days_in_roster(
        vacation_binary, CHAR_ZERO)
    number_of_work_days = min(4, 7 - vacation_for_week)
    number_of_off_days = max(2 - vacation_for_week, 0)
    number_of_reserve_days = 1 if vacation_for_week < 3 else 0

    # Define work days
    solver.Add(sum(workDays[worker, day]
               for day in DAYS_INDEX_8_14) == number_of_work_days)

    # Define off days
    solver.Add(sum(offDays[worker, day]
               for day in DAYS_INDEX_8_14) == number_of_off_days)

    # Define reserve days
    solver.Add(sum(reserve[worker, day]
               for day in DAYS_INDEX_8_14) == number_of_reserve_days)

    # Each day will be a working, off, reserve or a vacation day
    for day in DAYS_INDEX_8_14:
        solver.Add(workDays[worker, day] + offDays[worker, day] +
                   reserve[worker, day] + vacation[worker, day] + sickness[worker, day] == 1)

    # Each worker can only have shifts on workdays in the second week
    for day in DAYS_INDEX_8_14:
        solver.Add(sum(schedule[worker, (d - 1) * 3 + k]
                   for k in range(1, 4)) == workDays[worker, day])

    # Each worker can work at most one shift per day in the second week
    for day in DAYS_INDEX_8_14:
        solver.Add(sum(schedule[worker, (day - 1) * 3 + k]
                   for k in range(1, 4)) <= 1)

    # Each worker can work at most 2 night shifts in the second week
    solver.Add(sum(schedule[worker, (day - 1) * 3 + 3]
               for day in DAYS_INDEX_8_14) <= 2)

    if number_of_off_days > 0 and max_consecutive_no_vac_days > 1:
        # Ensure a reserve day follows a day off
        for day in DAYS_INDEX_8_13:
            solver.Add(offDays[worker, day + 1] >= reserve[worker, day])

        # Ensure a reserve day cannot be preceded by an off day
        for day in DAYS_INDEX_9_14:
            solver.Add(offDays[worker, day - 1] <= 1 - reserve[worker, day])

    # After night shifts, workers can't have morning or afternoon shift in both weeks
    for day in DAYS_INDEX_8_13:  # 1..13
        solver.Add(sum(schedule[worker, 3 + (day - 1) * 3 + k]
                   for k in range(3)) <= 1)


def get_min_workers(multiplier):
    min_workers = {
        22: 2, 23: 4, 24: 2, 25: 2, 26: 4, 27: 2, 28: 2, 29: 4, 30: 2, 31: 2,
        32: 4, 33: 2, 34: 2, 35: 4, 36: 2, 37: 1, 38: 2, 39: 1, 40: 1, 41: 2, 42: 1
    }

    min_workers = {key: value * multiplier for key,
                   value in min_workers.items()}
    return min_workers


def get_variables_for_model():
    return {}, {}, {}, {}, {}, {}


def optimize_schedule(number_of_users_to_solve, multiplier):

    solver = pywraplp.Solver.CreateSolver('SCIP')
    solver.SetSolverSpecificParametersAsString("display/verblevel = 4")
    solver.EnableOutput()

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
    current_week_sickness = {}

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
        current_week_sickness[username] = get_day_mapping(
            current_week_roster.sickness, DAY_INDEX_START, DAY_INDEX_END)

    # Parameters
    min_workers = get_min_workers(multiplier)

    # Variables
    schedule, reserve, workDays, offDays, vacation, sickness = get_variables_for_model()

    for worker in WORKERS:
        for shift in ROSTER_INDEX_1_42:
            schedule[worker, shift] = solver.BoolVar(f'schedule[{w},{s}]')

        for day in DAYS_INDEX_1_14:
            reserve[worker, day] = solver.BoolVar(f'reserve[{w},{d}]')
            workDays[worker, day] = solver.BoolVar(f'workDays[{w},{d}]')
            offDays[worker, day] = solver.BoolVar(f'offDays[{w},{d}]')
            vacation[worker, day] = solver.BoolVar(f'vacation[{w},{d}]')
            sickness[worker, day] = solver.BoolVar(f'sickness[{w},{d}]')

    for w in WORKERS:
        # Fix variables for the first week
        for shift in ROSTER_INDEX_1_21:
            schedule[worker, shift].SetBounds(
                int(last_week_schedules[worker][shift]), int(last_week_schedules[worker][shift]))
        for day in DAYS_INDEX_1_7:
            workDays[worker, day].SetBounds(
                int(last_week_work_days[worker][day]), int(last_week_work_days[worker][day]))
            offDays[worker, day].SetBounds(
                int(last_week_off_days[worker][day]), int(last_week_off_days[worker][day]))
            reserve[worker, day].SetBounds(
                int(last_week_reserve_days[worker][day]), int(last_week_reserve_days[worker][day]))

        # Fix variables for the second week
        for day in DAYS_INDEX_8_14:
            if int(current_week_vacation[worker][day - 7]) == 1 or int(current_week_sickness[worker][day - 7]) == 1:
                workDays[worker, day].SetBounds(0, 0)
                offDays[worker, day].SetBounds(0, 0)
                reserve[worker, day].SetBounds(0, 0)
                if int(current_week_vacation[worker][day - 7]) == 1:
                    vacation[worker, day].SetBounds(1, 1)
                else:
                    sickness[worker, day].SetBounds(1, 1)
            else:
                vacation[worker, day].SetBounds(0, 0)
                sickness[worker, day].sickness(0, 0)

    # Objective function: maximize the applications for the second week
    # TODO: add min worker for each day
    objective = solver.Objective()
    for worker in WORKERS:
        for shift in ROSTER_INDEX_22_42:
            coefficient = float(current_week_applications[worker][shift])
            objective.SetCoefficient(schedule[worker, shift], coefficient)

    objective.SetMaximization()

    # Constraints
    for worker in WORKERS:
        add_worker_constraints_to_solver(
            worker, solver, workDays, offDays, reserve, vacation, sickness, schedule, current_week_vacation)

    # Minimum required workers for each shift in the second week
    for shift in ROSTER_INDEX_22_42:
        solver.Add(sum(schedule[worker, shift]
                   for worker in WORKERS) >= min_workers[s])
        total_constraints += 1

    # Each day must have at least 2 reserve workers in the second week
    for day in DAYS_INDEX_8_14:
        solver.Add(sum(reserve[worker, day]
                   for worker in WORKERS) >= 2 * multiplier)
        total_constraints += 1

    # Solve the model
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        for worker in WORKERS:
            schedule_str = ""
            work_days_str = ""
            off_days_str = ""
            reserve_days_str = ""

            user = User.objects.get(username=worker)
            roster = Roster.objects.filter(
                week_number=current_week_number, owner=user).first()

            for shift in ROSTER_INDEX_22_42:
                schedule_str += str(
                    int(schedule[worker, shift].solution_value()))
            roster.schedule = schedule_str

            for day in DAYS_INDEX_8_14:
                work_days_str += str(int(workDays[worker,
                                     day].solution_value()))
                off_days_str += str(int(offDays[worker, day].solution_value()))
                reserve_days_str += str(
                    int(reserve[worker, day].solution_value()))

            roster.work_days = work_days_str
            roster.off_days = off_days_str
            roster.reserve_days = reserve_days_str
            roster.published = True
            roster.save()

        # Retrieve and print statistics
        print('Solver runtime (ms):', solver.WallTime())
        print('Number of constraints:', solver.NumConstraints())

    return status, solver.WallTime(), solver.NumConstraints()
