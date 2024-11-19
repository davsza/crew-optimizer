from typing import Dict, Tuple
from django.contrib.auth.models import User
from ortools.linear_solver import pywraplp

from .models import Roster
from .utils.common_fn import (
    get_day_mapping,
    get_roster_mapping,
    max_consecutive_days_in_roster,
    merge_roster_strings
)
from .utils.constants import CHAR_ZERO
from .utils.date_time_fn import get_current_week_number
from .utils.model_fn import get_rosters_by_week
from .utils.solver_constants import (
    DAYS_INDEX_1_14,
    DAYS_INDEX_1_6,
    DAYS_INDEX_1_7,
    DAYS_INDEX_2_7,
    DAYS_INDEX_8_13,
    DAYS_INDEX_8_14,
    DAYS_INDEX_9_14,
    FIRST_WEEK_DAY_INDEX_END,
    FIRST_WEEK_DAY_INDEX_START,
    SECOND_WEEK_DAY_INDEX_START,
    SECOND_WEEK_DAY_INDEX_END,
    ROSTER_INDEX_1_21,
    ROSTER_INDEX_1_42,
    ROSTER_INDEX_22_42,
    ROSTER_INDEX_START,
    ROSTER_INDEX_END,
)


def get_min_workers_both_weeks(multiplier: int) -> Dict[int, int]:
    """
    Calculates the minimum number of workers required for both weeks, scaled by a multiplier.

    Args:
        multiplier (int): A factor by which the base worker counts are multiplied.

    Returns:
        Dict[int, int]: A dictionary mapping day indices (1-42) to the minimum number of workers
        required.

    Notes:
        - Days 1 to 21 correspond to the first week, while days 22 to 42 correspond to the second
        week.
        - The input multiplier scales the base worker counts proportionally.
    """
    min_workers = {
        1: 2, 2: 4, 3: 2, 4: 2, 5: 4, 6: 2, 7: 2, 8: 4, 9: 2, 10: 2,
        11: 4, 12: 2, 13: 2, 14: 4, 15: 2, 16: 1, 17: 2, 18: 1, 19: 1, 20: 2,
        21: 1, 22: 2, 23: 4, 24: 2, 25: 2, 26: 4, 27: 2, 28: 2, 29: 4, 30: 2,
        31: 2, 32: 4, 33: 2, 34: 2, 35: 4, 36: 2, 37: 1, 38: 2, 39: 1, 40: 1,
        41: 2, 42: 1
    }

    return {key: value * multiplier for key, value in min_workers.items()}


def get_min_workers_second_week(multiplier: int) -> Dict[int, int]:
    """
    Calculates the minimum number of workers required for the second week, scaled by a multiplier.

    Args:
        multiplier (int): A factor by which the base worker counts are multiplied.

    Returns:
        Dict[int, int]: A dictionary mapping day indices (22-42) to the minimum number of workers
        required.

    Notes:
        - The second week consists of days 22 to 42.
        - The input multiplier scales the base worker counts proportionally.
    """
    min_workers = {
        22: 2, 23: 4, 24: 2, 25: 2, 26: 4, 27: 2, 28: 2, 29: 4, 30: 2,
        31: 2, 32: 4, 33: 2, 34: 2, 35: 4, 36: 2, 37: 1, 38: 2, 39: 1, 40: 1,
        41: 2, 42: 1
    }

    return {key: value * multiplier for key, value in min_workers.items()}


def reoptimize_schedule_after_sickness(
    number_of_users_to_solve: int,
    multiplier: int,
    day_index: int
) -> Tuple[int, int, int]:
    """
    Reoptimizes worker shift schedules for two weeks, adjusting for sickness, vacation,
    and other constraints while ensuring proper staffing and fairness.

    Args:
        number_of_users_to_solve (int): Number of workers to include in the optimization.
        multiplier (int): Factor for determining the number of reserve workers per day.
        day_index (int): The specific day (1-based index) up to which the schedule should be
        optimized.

    Returns:
        Tuple[int, int, int]: 
            - Solver status (int): Indicates whether an optimal solution was found.
            - Solver runtime (int): Time taken by the solver to run (in milliseconds).
            - Number of constraints (int): The total number of constraints in the model.

    Notes:
        - This function uses Google OR-Tools' SCIP solver for optimization.
        - Adjusts both current and next week's rosters, depending on `day_index`.
        - Outputs updated schedules to the database.
    """

    solver = pywraplp.Solver.CreateSolver('SCIP')
    solver.SetSolverSpecificParametersAsString("display/verblevel = 4")
    solver.EnableOutput()

    var_schedule = {}
    var_work_days = {}
    var_off_days = {}
    var_reserve_days = {}
    var_vacation = {}
    var_sickness = {}

    p_work_days = {}
    p_off_days = {}
    p_reserve = {}

    current_week_number = get_current_week_number(0)
    next_week_number = get_current_week_number(1)
    current_week_rosters = get_rosters_by_week(
        current_week_number, number_of_users_to_solve)
    next_week_rosters = get_rosters_by_week(
        next_week_number, number_of_users_to_solve)

    schedules = {}
    work_days = {}
    off_days = {}
    reserve_days = {}
    vacation = {}
    sickness = {}

    fw_reserve_call_in = {}
    sw_reserve_call_in = {}

    workers = []

    for current_week_roster, next_week_roster in zip(current_week_rosters, next_week_rosters):
        username = current_week_roster.owner.username
        workers.append(username)

        schedules[username] = get_roster_mapping(
            current_week_roster.schedule + next_week_roster.schedule,
            1,
            ROSTER_INDEX_END
        )
        work_days[username] = get_day_mapping(
            current_week_roster.work_days + next_week_roster.work_days,
            FIRST_WEEK_DAY_INDEX_START,
            SECOND_WEEK_DAY_INDEX_END
        )
        off_days_roster_current_week = merge_roster_strings(
            current_week_roster.off_days,
            current_week_roster.reserve_call_in_days,
            current_week_roster.day_off_call_in_days
        )
        off_days_roster_next_week = merge_roster_strings(
            next_week_roster.off_days,
            next_week_roster.reserve_call_in_days,
            next_week_roster.day_off_call_in_days
        )
        off_days[username] = get_day_mapping(
            off_days_roster_current_week + off_days_roster_next_week,
            FIRST_WEEK_DAY_INDEX_START, SECOND_WEEK_DAY_INDEX_END
        )
        reserve_days[username] = get_day_mapping(
            current_week_roster.reserve_days + next_week_roster.reserve_days,
            FIRST_WEEK_DAY_INDEX_START,
            SECOND_WEEK_DAY_INDEX_END
        )
        vacation[username] = get_day_mapping(
            current_week_roster.vacation + next_week_roster.vacation,
            FIRST_WEEK_DAY_INDEX_START,
            SECOND_WEEK_DAY_INDEX_END
        )
        sickness[username] = get_day_mapping(
            current_week_roster.sickness + next_week_roster.sickness,
            FIRST_WEEK_DAY_INDEX_START,
            SECOND_WEEK_DAY_INDEX_END
        )

        fw_reserve_call_in[username] = current_week_roster.reserve_call_in
        sw_reserve_call_in[username] = next_week_roster.reserve_call_in

    min_workers = get_min_workers_both_weeks(multiplier)

    # Init variables
    for worker in workers:
        for shift in ROSTER_INDEX_1_42:
            var_schedule[worker, shift] = solver.BoolVar(
                f'var_schedule[{worker},{shift}]')

        for day in DAYS_INDEX_1_14:
            var_work_days[worker, day] = solver.BoolVar(
                f'var_work_days[{worker},{day}]')
            var_off_days[worker, day] = solver.BoolVar(
                f'var_off_days[{worker},{day}]')
            var_reserve_days[worker, day] = solver.BoolVar(
                f'var_reserve_days[{worker},{day}]')
            var_vacation[worker, day] = solver.BoolVar(
                f'var_vacation[{worker},{day}]')
            var_sickness[worker, day] = solver.BoolVar(
                f'var_sickness[{worker},{day}]')

            p_work_days[worker, day] = solver.BoolVar(
                f'p_work_days[{worker},{day}]')
            p_off_days[worker, day] = solver.BoolVar(
                f'p_off_days[{worker},{day}]')
            p_reserve[worker, day] = solver.BoolVar(
                f'p_reserve[{worker},{day}]')

    shift_range = (day_index - 1) * 3 + 1
    day_range = day_index

    for worker in workers:
        # Fix variables until the day index
        for shift in range(1, shift_range):
            var_schedule[worker, shift].SetBounds(
                int(schedules[worker][shift]), int(schedules[worker][shift]))

        for day in range(1, day_range):
            var_work_days[worker, day].SetBounds(
                int(work_days[worker][day]), int(work_days[worker][day]))
            var_off_days[worker, day].SetBounds(
                int(off_days[worker][day]), int(off_days[worker][day]))
            var_reserve_days[worker, day].SetBounds(
                int(reserve_days[worker][day]), int(reserve_days[worker][day]))

        for day in DAYS_INDEX_1_14:
            if int(vacation[worker][day]) == 1 or int(sickness[worker][day]) == 1:
                var_work_days[worker, day].SetBounds(0, 0)
                var_off_days[worker, day].SetBounds(0, 0)
                var_reserve_days[worker, day].SetBounds(0, 0)
                if int(vacation[worker][day]) == 1:
                    var_vacation[worker, day].SetBounds(1, 1)
                else:
                    var_sickness[worker, day].SetBounds(1, 1)
            else:
                var_vacation[worker, day].SetBounds(0, 0)
                var_sickness[worker, day].SetBounds(0, 0)

    e, f, g = 10, 50, 20

    objective = solver.Objective()
    for worker in workers:
        for shift in ROSTER_INDEX_1_42:
            coefficient = float(schedules[worker][shift])
            objective.SetCoefficient(var_schedule[worker, shift], coefficient)

        for day in DAYS_INDEX_1_14:
            coefficient = float(work_days[worker][day])
            objective.SetCoefficient(var_work_days[worker, day], coefficient)

            coefficient = float(off_days[worker][day])
            objective.SetCoefficient(var_off_days[worker, day], coefficient)

            coefficient = float(reserve_days[worker][day])
            objective.SetCoefficient(var_reserve_days[worker, day], coefficient)

            objective.SetCoefficient(p_work_days[worker, day], -e)
            objective.SetCoefficient(p_off_days[worker, day], -f)
            objective.SetCoefficient(p_reserve[worker, day], -g)

    objective.SetMaximization()

    for worker in workers:
        fw_vacation = sum(int(vac)
                          for vac in list(vacation[worker].values())[:7])
        sw_vacation = sum(int(vac)
                          for vac in list(vacation[worker].values())[-7:])
        fw_sickness = sum(int(sick)
                          for sick in list(sickness[worker].values())[:7])
        sw_sickness = sum(int(sick)
                          for sick in list(sickness[worker].values())[-7:])
        fw_vacation_binary = ''.join(list(vacation[worker].values())[:7])
        sw_vacation_binary = ''.join(list(vacation[worker].values())[-7:])
        fw_sickness_binary = ''.join(list(sickness[worker].values())[:7])
        sw_sickness_binary = ''.join(list(sickness[worker].values())[-7:])
        fw_max_consecutive_number_of_vac_days = max_consecutive_days_in_roster(
            fw_vacation_binary, CHAR_ZERO)
        sw_max_consecutive_number_of_vac_days = max_consecutive_days_in_roster(
            sw_vacation_binary, CHAR_ZERO)
        fw_max_consecutive_number_of_sick_days = max_consecutive_days_in_roster(
            fw_sickness_binary, CHAR_ZERO)
        sw_max_consecutive_number_of_sick_days = max_consecutive_days_in_roster(
            sw_sickness_binary, CHAR_ZERO)
        fw_max_cnsc_num_vac_sick_days = max(
            fw_max_consecutive_number_of_vac_days, fw_max_consecutive_number_of_sick_days)
        sw_max_cnsc_num_vac_sick_days = max(
            sw_max_consecutive_number_of_vac_days, sw_max_consecutive_number_of_sick_days)
        fw_vac_sick_sum = fw_vacation + fw_sickness
        sw_vac_sick_sum = sw_vacation + sw_sickness
        fw_number_of_work_days = min(4, 7 - fw_vac_sick_sum)
        fw_number_of_off_days = max(2 - fw_vac_sick_sum, 0)
        fw_number_of_reserve_days = 1 if fw_vac_sick_sum < 3 else 0
        sw_number_of_work_days = min(4, 7 - sw_vac_sick_sum)
        sw_number_of_off_days = max(2 - sw_vac_sick_sum, 0)
        sw_number_of_reserve_days = 1 if sw_vac_sick_sum < 3 else 0
        
        for day in DAYS_INDEX_1_14:
            solver.Add(p_work_days[worker, day] >= 0)
            solver.Add(p_off_days[worker, day] >= 0)
            solver.Add(p_reserve[worker, day] >= 0)

        # Cut on second week
        if day_index > 7:
            # Define work days
            solver.Add(sum((var_work_days[worker, day] - p_work_days[worker, day])
                       for day in DAYS_INDEX_8_14) == sw_number_of_work_days)

            # Define off days
            solver.Add(sum((var_off_days[worker, day] + p_off_days[worker, day])
                       for day in DAYS_INDEX_8_14) == sw_number_of_off_days)

            # Define reserve days
            solver.Add(sum((var_reserve_days[worker, day] + p_reserve[worker, day])
                       for day in DAYS_INDEX_8_14) == sw_number_of_reserve_days)

            # Each day must have at least 2 reserve workers
            for day in range(day_index, 15):
                solver.Add(sum(var_reserve_days[worker, day]
                           for worker in workers) >= 2 * multiplier)

        # Cut on first week
        else:
            # Define work days
            solver.Add(sum((var_work_days[worker, day] - p_work_days[worker, day])
                       for day in DAYS_INDEX_1_7) == fw_number_of_work_days)
            solver.Add(sum(var_work_days[worker, day]
                       for day in DAYS_INDEX_8_14) == sw_number_of_work_days)

            # Define off days
            solver.Add(sum((var_off_days[worker, day] + p_off_days[worker, day])
                       for day in DAYS_INDEX_1_7) == fw_number_of_off_days)
            solver.Add(sum(var_off_days[worker, day]
                       for day in DAYS_INDEX_8_14) == sw_number_of_off_days)

            # Define reserve days
            solver.Add(sum((var_reserve_days[worker, day] + p_reserve[worker, day])
                       for day in DAYS_INDEX_1_7) == fw_number_of_reserve_days)
            solver.Add(sum(var_reserve_days[worker, day]
                       for day in DAYS_INDEX_8_14) == sw_number_of_reserve_days)

            # Each day must have at least 2 reserve workers
            for day in range(day_range, 8):
                solver.Add(sum(var_reserve_days[worker, day]
                           for worker in workers) >= 2 * multiplier)
            for day in DAYS_INDEX_8_14:
                solver.Add(sum(var_reserve_days[worker, day]
                           for worker in workers) >= 2 * multiplier)

        # Each day will be a working, off, reserve or a vacation day
        for day in DAYS_INDEX_1_14:
            solver.Add(var_work_days[worker, day] +
                       var_off_days[worker, day] +
                       var_reserve_days[worker, day] +
                       var_vacation[worker, day] +
                       var_sickness[worker, day] == 1)

        # Each worker can only have shifts on workdays
        for day in DAYS_INDEX_1_14:
            solver.Add(sum(var_schedule[worker, (day - 1) * 3 + k]
                       for k in range(1, 4)) == var_work_days[worker, day])

        # Each worker can work at most one shift per day
        for day in DAYS_INDEX_1_14:
            solver.Add(sum(var_schedule[worker, (day - 1) * 3 + k]
                       for k in range(1, 4)) <= 1)

        if (
            fw_number_of_off_days > 0 and
            fw_max_cnsc_num_vac_sick_days > 1 and
            not fw_reserve_call_in[worker]
        ):
            # Ensure a reserve day follows a day off
            for day in DAYS_INDEX_1_6:
                solver.Add(var_off_days[worker, day + 1]
                           >= var_reserve_days[worker, day])

            # Ensure a reserve day cannot be preceded by an off day
            for day in DAYS_INDEX_2_7:
                solver.Add(var_off_days[worker, day - 1]
                           <= 1 - var_reserve_days[worker, day])

            solver.Add(sum(var_schedule[worker, (day - 1) * 3 + 3]
                       for day in DAYS_INDEX_1_7) <= 2)

        if (
            sw_number_of_off_days > 0 and
            sw_max_cnsc_num_vac_sick_days > 1 and
            not sw_reserve_call_in[worker]
        ):
            # Ensure a reserve day follows a day off
            for day in DAYS_INDEX_8_13:
                solver.Add(var_off_days[worker, day + 1]
                           >= var_reserve_days[worker, day])

            # Ensure a reserve day cannot be preceded by an off day
            for day in DAYS_INDEX_9_14:
                solver.Add(var_off_days[worker, day - 1]
                           <= 1 - var_reserve_days[worker, day])

            # Each worker can work at most 2 night shifts
            solver.Add(sum(var_schedule[worker, (day - 1) * 3 + 3]
                           for day in DAYS_INDEX_8_14) <= 2)

        # After night shifts, workers can't have morning or afternoon shift in both weeks
        for day in DAYS_INDEX_8_13:  # 1..13
            solver.Add(sum(var_schedule[worker, 3 + (day - 1) * 3 + k]
                       for k in range(3)) <= 1)

    # Minimum required workers for each shift
    for shift in ROSTER_INDEX_1_42:
        solver.Add(sum(var_schedule[worker, shift]
                   for worker in workers) >= min_workers[shift])

    # Solve the model
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        for worker in workers:
            res_schedule = ""
            res_work_days = ""
            res_off_days = ""
            res_reserve_days = ""

            user = User.objects.get(username=worker)

            if day_index > 7:
                roster = Roster.objects.get(
                    week_number=next_week_number, owner=user)

                for shift in ROSTER_INDEX_22_42:
                    res_schedule += str(
                        int(var_schedule[worker, shift].solution_value()))
                roster.schedule = res_schedule

                for day in DAYS_INDEX_8_14:
                    res_work_days += str(
                        int(var_work_days[worker, day].solution_value()))
                    res_off_days += str(
                        int(var_off_days[worker, day].solution_value()))
                    res_reserve_days += str(
                        int(var_reserve_days[worker, day].solution_value()))

                roster.work_days = res_work_days
                roster.off_days = res_off_days
                roster.reserve_days = res_reserve_days
                roster.published = True
                roster.save()
            else:
                roster = Roster.objects.get(
                    week_number=current_week_number, owner=user)

                for shift in ROSTER_INDEX_1_21:
                    res_schedule += str(
                        int(var_schedule[worker, shift].solution_value()))
                roster.schedule = res_schedule

                for day in DAYS_INDEX_1_7:
                    res_work_days += str(
                        int(var_work_days[worker, day].solution_value()))
                    res_off_days += str(
                        int(var_off_days[worker, day].solution_value()))
                    res_reserve_days += str(
                        int(var_reserve_days[worker, day].solution_value()))

                roster.work_days = res_work_days
                roster.off_days = res_off_days
                roster.reserve_days = res_reserve_days
                roster.published = True
                roster.save()

                roster = Roster.objects.get(
                    week_number=next_week_number, owner=user)

                for shift in ROSTER_INDEX_22_42:
                    res_schedule += str(
                        int(var_schedule[worker, shift].solution_value()))
                roster.schedule = res_schedule

                for day in DAYS_INDEX_8_14:
                    res_work_days += str(
                        int(var_work_days[worker, day].solution_value()))
                    res_off_days += str(
                        int(var_off_days[worker, day].solution_value()))
                    res_reserve_days += str(
                        int(var_reserve_days[worker, day].solution_value()))

                roster.work_days = res_work_days
                roster.off_days = res_off_days
                roster.reserve_days = res_reserve_days
                roster.published = True
                roster.save()

        # Retrieve and print statistics
        print('Solver runtime (ms):', solver.WallTime())
        print('Number of constraints:', solver.NumConstraints())

    return status, solver.WallTime(), solver.NumConstraints()


def optimize_schedule(number_of_users_to_solve: int, multiplier: float) -> Tuple[int, int, int]:
    """
    Optimizes the worker schedule for the second week based on predefined rules, constraints, 
    and applications using a linear programming solver.

    Args:
        number_of_users_to_solve (int): The number of users to include in the optimization.
        multiplier (float): A scaling factor affecting certain constraints (e.g., reserve workers).

    Returns:
        Tuple[int, int, int]: A tuple containing:
            - `status` (int): The solver's status (e.g., `pywraplp.Solver.OPTIMAL` for a successful
            solution).
            - `solver.WallTime()` (int): The runtime of the solver in milliseconds.
            - `solver.NumConstraints()` (int): The number of constraints applied to the solver.
    """

    solver = pywraplp.Solver.CreateSolver('SCIP')
    solver.SetSolverSpecificParametersAsString("display/verblevel = 4")
    solver.EnableOutput()

    # Variables
    var_schedule = {}
    var_work_days = {}
    var_off_days = {}
    var_reserve_days = {}
    var_vacation = {}
    var_sickness = {}

    next_week_number = get_current_week_number(1)
    application_week_number = get_current_week_number(2)
    next_week_rosters = get_rosters_by_week(
        next_week_number, number_of_users_to_solve)
    application_week_rosters = get_rosters_by_week(
        application_week_number, number_of_users_to_solve)

    next_week_schedules = {}
    application_week_applications = {}
    next_week_work_days = {}
    next_week_off_days = {}
    next_week_reserve_days = {}
    application_week_vacation = {}
    application_week_sickness = {}

    workers = []

    for next_week_roster, application_week_roster in zip(
        next_week_rosters,
        application_week_rosters
    ):
        username = application_week_roster.owner.username
        workers.append(username)

        application_week_applications[username] = get_roster_mapping(
            application_week_roster.application,
            ROSTER_INDEX_START,
            ROSTER_INDEX_END
        )
        next_week_schedules[username] = get_roster_mapping(
            next_week_roster.schedule,
            ROSTER_INDEX_START,
            ROSTER_INDEX_END,
            ROSTER_INDEX_START - 1
        )
        next_week_work_days[username] = get_day_mapping(
            next_week_roster.work_days,
            FIRST_WEEK_DAY_INDEX_START,
            FIRST_WEEK_DAY_INDEX_END
        )
        next_week_off_days[username] = get_day_mapping(
            next_week_roster.off_days,
            FIRST_WEEK_DAY_INDEX_START,
            FIRST_WEEK_DAY_INDEX_END
        )
        next_week_reserve_days[username] = get_day_mapping(
            next_week_roster.reserve_days,
            FIRST_WEEK_DAY_INDEX_START,
            FIRST_WEEK_DAY_INDEX_END
        )
        application_week_vacation[username] = get_day_mapping(
            application_week_roster.vacation,
            SECOND_WEEK_DAY_INDEX_START,
            SECOND_WEEK_DAY_INDEX_END
        )
        application_week_sickness[username] = get_day_mapping(
            application_week_roster.sickness,
            SECOND_WEEK_DAY_INDEX_START,
            SECOND_WEEK_DAY_INDEX_END
        )

    min_workers = get_min_workers_second_week(multiplier)

    # Init variables
    for worker in workers:
        for shift in ROSTER_INDEX_1_42:
            var_schedule[worker, shift] = solver.BoolVar(
                f'var_schedule[{worker},{shift}]')

        for day in DAYS_INDEX_1_14:
            var_work_days[worker, day] = solver.BoolVar(
                f'var_work_days[{worker},{day}]')
            var_off_days[worker, day] = solver.BoolVar(
                f'var_off_days[{worker},{day}]')
            var_reserve_days[worker, day] = solver.BoolVar(
                f'var_reserve_days[{worker},{day}]')
            var_vacation[worker, day] = solver.BoolVar(
                f'var_vacation[{worker},{day}]')
            var_sickness[worker, day] = solver.BoolVar(
                f'var_sickness[{worker},{day}]')

    for worker in workers:
        # Fix variables for the first week
        for shift in ROSTER_INDEX_1_21:
            var_schedule[worker, shift].SetBounds(
                int(next_week_schedules[worker][shift]), int(next_week_schedules[worker][shift]))

        for day in DAYS_INDEX_1_7:
            var_work_days[worker, day].SetBounds(
                int(next_week_work_days[worker][day]), int(next_week_work_days[worker][day]))
            var_off_days[worker, day].SetBounds(
                int(next_week_off_days[worker][day]), int(next_week_off_days[worker][day]))
            var_reserve_days[worker, day].SetBounds(
                int(next_week_reserve_days[worker][day]), int(next_week_reserve_days[worker][day]))

        # Fix variables for the second week
        for day in DAYS_INDEX_8_14:
            if (
                int(application_week_vacation[worker][day]) == 1 or
                int(application_week_sickness[worker][day]) == 1
            ):
                var_work_days[worker, day].SetBounds(0, 0)
                var_off_days[worker, day].SetBounds(0, 0)
                var_reserve_days[worker, day].SetBounds(0, 0)
                if int(application_week_vacation[worker][day]) == 1:
                    var_vacation[worker, day].SetBounds(1, 1)
                else:
                    var_sickness[worker, day].SetBounds(1, 1)
            else:
                var_vacation[worker, day].SetBounds(0, 0)
                var_sickness[worker, day].SetBounds(0, 0)

    # Objective function: maximize the applications for the second week
    objective = solver.Objective()
    for worker in workers:
        for shift in ROSTER_INDEX_22_42:
            coefficient = float(application_week_applications[worker][shift])
            objective.SetCoefficient(var_schedule[worker, shift], coefficient)

    objective.SetMaximization()

    # Constraints
    for worker in workers:
        vacation_for_week = sum(
            int(vac) for vac in application_week_vacation[worker].values())
        sickness_for_week = sum(
            int(sick) for sick in application_week_sickness[worker].values())
        vacation_binary = ''.join(application_week_vacation[worker].values())
        sickness_binary = ''.join(application_week_sickness[worker].values())
        max_consecutive_number_of_vac_days = max_consecutive_days_in_roster(
            vacation_binary, CHAR_ZERO)
        max_consecutive_number_of_sick_days = max_consecutive_days_in_roster(
            sickness_binary, CHAR_ZERO)
        max_cnsc_num_vac_sick_days = max(
            max_consecutive_number_of_vac_days, max_consecutive_number_of_sick_days)
        vac_sick_sum = vacation_for_week + sickness_for_week
        number_of_work_days = min(4, 7 - vac_sick_sum)
        number_of_off_days = max(2 - vac_sick_sum, 0)
        number_of_reserve_days = 1 if vac_sick_sum < 3 else 0

        # Define work days
        solver.Add(sum(var_work_days[worker, day]
                   for day in DAYS_INDEX_8_14) == number_of_work_days)

        # Define off days
        solver.Add(sum(var_off_days[worker, day]
                   for day in DAYS_INDEX_8_14) == number_of_off_days)

        # Define reserve days
        solver.Add(sum(var_reserve_days[worker, day]
                   for day in DAYS_INDEX_8_14) == number_of_reserve_days)

        # Each day will be a working, off, reserve or a vacation day
        for day in DAYS_INDEX_8_14:
            solver.Add(var_work_days[worker, day] +
                       var_off_days[worker, day] +
                       var_reserve_days[worker, day] +
                       var_vacation[worker, day] +
                       var_sickness[worker, day] == 1)

        # Each worker can only have shifts on workdays in the second week
        for day in DAYS_INDEX_8_14:
            solver.Add(sum(var_schedule[worker, (day - 1) * 3 + k]
                       for k in range(1, 4)) == var_work_days[worker, day])

        # Each worker can work at most one shift per day in the second week
        for day in DAYS_INDEX_8_14:
            solver.Add(sum(var_schedule[worker, (day - 1) * 3 + k]
                       for k in range(1, 4)) <= 1)

        # Each worker can work at most 2 night shifts in the second week
        solver.Add(sum(var_schedule[worker, (day - 1) * 3 + 3]
                   for day in DAYS_INDEX_8_14) <= 2)

        if number_of_off_days > 0 and max_cnsc_num_vac_sick_days > 1:
            # Ensure a reserve day follows a day off
            for day in DAYS_INDEX_8_13:
                solver.Add(var_off_days[worker, day + 1]
                           >= var_reserve_days[worker, day])

            # Ensure a reserve day cannot be preceded by an off day
            for day in DAYS_INDEX_9_14:
                solver.Add(var_off_days[worker, day - 1]
                           <= 1 - var_reserve_days[worker, day])

        # After night shifts, workers can't have morning or afternoon shift in both weeks
        for day in DAYS_INDEX_8_13:  # 1..13
            solver.Add(sum(var_schedule[worker, 3 + (day - 1) * 3 + k]
                       for k in range(3)) <= 1)

    # Minimum required workers for each shift in the second week
    for shift in ROSTER_INDEX_22_42:
        solver.Add(sum(var_schedule[worker, shift]
                   for worker in workers) >= min_workers[shift])

    # Each day must have at least 2 reserve workers in the second week
    for day in DAYS_INDEX_8_14:
        solver.Add(sum(var_reserve_days[worker, day]
                   for worker in workers) >= 2 * multiplier)

    # Solve the model
    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        for worker in workers:
            res_schedule = ""
            res_work_days = ""
            res_off_days = ""
            res_reserve_days = ""

            user = User.objects.get(username=worker)
            roster = Roster.objects.get(
                week_number=application_week_number, owner=user)

            for shift in ROSTER_INDEX_22_42:
                res_schedule += str(int(var_schedule[worker,
                                    shift].solution_value()))
            roster.schedule = res_schedule

            for day in DAYS_INDEX_8_14:
                res_work_days += str(
                    int(var_work_days[worker, day].solution_value()))
                res_off_days += str(int(var_off_days[worker,
                                    day].solution_value()))
                res_reserve_days += str(
                    int(var_reserve_days[worker, day].solution_value()))

            roster.work_days = res_work_days
            roster.off_days = res_off_days
            roster.reserve_days = res_reserve_days
            roster.published = True
            roster.save()

        # Retrieve and print statistics
        print('Solver runtime (ms):', solver.WallTime())
        print('Number of constraints:', solver.NumConstraints())

    return status, solver.WallTime(), solver.NumConstraints()
