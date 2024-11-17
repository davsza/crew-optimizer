import json
import random
from datetime import date, datetime
from typing import Optional, Tuple

from django.contrib.auth.models import User

from api.models import Roster
from .date_time_fn import current_dt, get_current_week_number
from .constants import (
    CHAR_ONE,
    CHAR_ZERO,
    DAYS_IN_WEEK,
    MAX_VACATION_CLAM_PER_YEAR
)
from .message_fn import (
    get_too_much_claimed_vacation_warning_msg,
    get_vacation_claim_msg,
    get_sickness_claim_msg
)
from .model_fn import (
    get_roster_by_user_and_week_number,
    get_rosters_by_week
)
from .common_fn import (
    replace_string_from_to_with_char,
    get_default_days_str,
    contains_character_from_index
)
from ..solver import reoptimize_schedule_after_sickness


def get_vacation_and_sick_data(json_input: str) -> Tuple[date, date, bool, str, Optional[User]]:
    """
    Extract vacation and sick leave data from a JSON input string.

    This function parses the provided JSON input to extract information related to a user's 
    vacation or sick leave, including the start and end dates, mode of leave, and whether the 
    leave should be saved or not. It also retrieves the user object if specified in the input.

    Args:
        json_input (str): A JSON-formatted string containing vacation or sick leave data.

    Returns:
        Tuple[date, date, bool, str, Optional[User]]: A tuple containing:
            - start_date (date): The start date of the vacation/sick leave.
            - end_date (date): The end date of the vacation/sick leave.
            - save (bool): Whether the leave should be saved or not.
            - mode (str): The mode of the leave (e.g., vacation or sick).
            - user (Optional[User]): The user associated with the leave, or None if no user is specified.
    """
    data = json.loads(json_input)
    vacation = data['vacation_sick']
    today = current_dt()

    start_date = datetime.strptime(
        vacation['start'], '%d-%m').replace(year=today.year).date()
    end_date = datetime.strptime(
        vacation['end'], '%d-%m').replace(year=today.year).date()

    mode = vacation['mode']

    if 'save' in vacation:
        save = vacation['save']
        user = None

    else:
        save = False
        user = User.objects.get(username=vacation["user"])

    return start_date, end_date, save, mode, user


def get_claimed_vacation_by_user_in_year(user: User, year: int) -> int:
    """
    Calculate the total number of vacation days claimed by a user in a given year.

    This function iterates over all the rosters for a specific user in the given year,
    counts the number of '1' characters (representing claimed vacation days) in the 
    'vacation' field of each roster, and returns the total number of claimed vacation days.

    Args:
        user (Type[User]): The user whose vacation claims are being calculated.
        year (int): The year to filter the rosters by.

    Returns:
        int: The total number of vacation days claimed by the user in the given year.
    """
    rosters = Roster.objects.filter(owner=user, year=year)
    return sum(str(roster.vacation).count(CHAR_ONE) for roster in rosters)


def vacation_claim(
    user: User,
    year: int,
    week_number: int,
    first_day_of_week: int,
    claim: bool,
    claim_length: int,
    start_date: datetime,
    end_date: datetime
) -> str:
    """
    Handles vacation claims for a user in a given year and week.

    This function checks whether the user can claim the requested vacation based on
    the maximum vacation days allowed per year, updates the roster accordingly,
    and returns a message indicating the result.

    Args:
        user (User): The user requesting the vacation.
        year (int): The year for the vacation claim.
        week_number (int): The week number of the vacation claim.
        first_day_of_week (int): The starting day of the week (1 for Monday, 7 for Sunday).
        claim (bool): Whether the user is claiming (True) or canceling (False) the vacation.
        claim_length (int): The number of days the user wants to claim or cancel.
        start_date (datetime): The start date of the vacation period.
        end_date (datetime): The end date of the vacation period.

    Returns:
        str: A message indicating the outcome of the vacation claim or cancellation.
    """
    claimed_vacation = get_claimed_vacation_by_user_in_year(user, year)

    if claim and claimed_vacation + claim_length > MAX_VACATION_CLAM_PER_YEAR:
        msg = get_too_much_claimed_vacation_warning_msg(
            claim_length, MAX_VACATION_CLAM_PER_YEAR, claimed_vacation)
        return msg

    replace_with = CHAR_ONE if claim else CHAR_ZERO
    roster = get_roster_by_user_and_week_number(user, week_number)
    vac_claim_in_week = DAYS_IN_WEEK - first_day_of_week + 1
    first_pos = first_day_of_week - 1

    if first_day_of_week + claim_length - 1 > 7:
        last_pos = 7
    else:
        last_pos = first_day_of_week + claim_length - 1

    roster.vacation = replace_string_from_to_with_char(
        roster.vacation, first_pos, last_pos, replace_with)

    if replace_with == CHAR_ONE:
        roster.application = replace_string_from_to_with_char(
            roster.application, first_pos * 3, last_pos * 3, CHAR_ZERO)

    roster.save()

    vacation_length = claim_length - vac_claim_in_week

    while vacation_length > 0:
        week_number += 1
        roster = get_roster_by_user_and_week_number(user, week_number)

        if vacation_length > 7:
            roster.vacation = replace_string_from_to_with_char(
                roster.vacation, 0, 7, replace_with)

        else:
            roster.vacation = replace_string_from_to_with_char(
                roster.vacation, 0, vacation_length, replace_with)

        vacation_length -= DAYS_IN_WEEK
        roster.save()

    msg = get_vacation_claim_msg(claim, start_date, end_date)
    return msg


def get_user_for_reserve(
    users,
    year: int,
    week_number: int,
    day_index: int,
    shift_index: int
) -> User:
    """
    Selects a user for a reserve shift based on their call-in history and schedule.

    The function first determines which user has the fewest reserve call-ins, excluding users
    who have already worked a shift on the day in question, and then randomly selects from them.

    Args:
        users (QuerySet[User]): A list of users eligible for the reserve shift.
        year (int): The year of the roster.
        week_number (int): The week number for which the reserve shift is being requested.
        day_index (int): The index of the day in the current week (0 = Monday, 6 = Sunday).
        shift_index (int): The shift index (0 = morning, 1 = afternoon, 2 = night).

    Returns:
        User: The selected user for the reserve shift.
    """
    call_ins = {
        user: sum(1 for roster in Roster.objects.filter(
            owner=user, year=year) if roster.reserve_call_in)
        for user in users
    }

    min_call_in = min(call_ins.values())

    users_with_lowest_call_ins = [
        user
        for user, reserve_call_ins in call_ins.items() 
        if reserve_call_ins == min_call_in
    ]

    users_to_exclude = []

    if shift_index == 0:  # Morning shift
        if day_index == 0:  # Monday
            prev_week_rosters = Roster.objects.filter(
                owner__in=users, week_number=week_number - 1)
            for prev_week_roster in prev_week_rosters:
                if prev_week_roster.work_days[6] == "1" and prev_week_roster.schedule[20] == "1":
                    users_to_exclude.append(prev_week_roster.owner)

        else:
            current_week_rosters = Roster.objects.filter(
                owner__in=users, week_number=week_number)
            for current_week_roster in current_week_rosters:
                if current_week_roster.work_days[day_index - 1] == "1" and current_week_roster.schedule[(day_index - 1) * 3 + 2] == "1":
                    users_to_exclude.append(current_week_roster.owner)

    eligible_users = [
        user
        for user in users_with_lowest_call_ins
        if user not in users_to_exclude
    ]

    return random.choice(eligible_users) if eligible_users else None


def sickness_claim(
    user: User,
    year: int,
    week_number: int,
    sickness_first_day_of_week: int,
    sickness_length: int,
    start_date: date,
    end_date: date,
    first_day_for_application_week: date
) -> str:
    """
    Handles a user's sickness claim by updating their work schedules, checking for reserve users,
    and adjusting rosters for affected weeks. Ensures compliance with the application's policies.

    Args:
        user (object): The user submitting the sickness claim.
        year (int): The year of the sickness claim.
        week_number (int): The starting week number of the sickness claim.
        sickness_first_day_of_week (int): The first day of the week when the sickness starts (1-7).
        sickness_length (int): The total length of the sickness in days.
        start_date (date): The starting date of the sickness.
        end_date (date): The ending date of the sickness.
        first_day_for_application_week (date): The first day of the application week.

    Returns:
        str: A message summarizing the sickness claim's outcome.
    """
    sickness_claim_in_week = min(DAYS_IN_WEEK - sickness_first_day_of_week + 1, (end_date - start_date).days + 1)
    weeks_calculated = week_number - get_current_week_number(0)
    recalculate = False
    day_off_call_in_index = -1

    first_pos = sickness_first_day_of_week - 1

    if sickness_first_day_of_week + sickness_length - 1 > 7:
        last_pos = 7
    else:
        last_pos = sickness_first_day_of_week + sickness_length - 1

    # sickness for current and next week
    while sickness_length > 0 and weeks_calculated < 2 and not recalculate and start_date < first_day_for_application_week:
        user_roster = Roster.objects.get(owner=user, week_number=week_number)
        rosters = get_rosters_by_week(week_number)

        for day_index in range(first_pos, last_pos):
            users_for_reserve = [roster.owner for roster in [
                roster for roster in rosters if roster.reserve_days[day_index] == "1"]]

            if users_for_reserve:
                if user_roster.work_days[day_index] == "1":
                    shift_index = user_roster.schedule[day_index * 3:day_index * 3 + 3].index("1")

                    reserve_user = get_user_for_reserve(users_for_reserve, year, week_number, day_index, shift_index)

                    if reserve_user is None:
                        recalculate = True
                        day_off_call_in_index = day_index
                        break

                    reserve_user_roster = Roster.objects.get(
                        owner=reserve_user, week_number=week_number)

                    reserve_user_roster.reserve_call_in_days = reserve_user_roster.reserve_days
                    reserve_user_roster.reserve_days = get_default_days_str(CHAR_ZERO)
                    reserve_user_roster.reserve_call_in = True
                    reserve_user_roster.schedule = (
                        reserve_user_roster.schedule[:day_index * 3 + shift_index] +
                        CHAR_ONE +
                        reserve_user_roster.schedule[day_index * 3 + shift_index + 1:]
                    )

                    user_roster.schedule = (
                        user_roster.schedule[:day_index * 3 + shift_index] +
                        CHAR_ZERO +
                        user_roster.schedule[day_index * 3 + shift_index + 1:]
                    )
                    user_roster.work_days = (
                        user_roster.work_days[:day_index] +
                        CHAR_ZERO +
                        user_roster.work_days[day_index + 1:]
                    )
                    # reserve_user_roster.save()

                else:
                    if user_roster.off_days[day_index] == "1":
                        user_roster.off_days = (
                            user_roster.off_days[:day_index] +
                            CHAR_ZERO +
                            user_roster.off_days[day_index + 1:]
                        )

                    if user_roster.reserve_days[day_index] == "1":
                        user_roster.reserve_days = (
                            user_roster.reserve_days[:day_index] + \
                            CHAR_ZERO +
                            user_roster.reserve_days[day_index + 1:]
                        )

                    if user_roster.vacation[day_index] == "1":
                        user_roster.vacation = (
                            user_roster.vacation[:day_index] +
                            CHAR_ZERO +
                            user_roster.vacation[day_index + 1:]
                        )

                user_roster.sickness = (
                    user_roster.sickness[:day_index] +
                    CHAR_ONE +
                    user_roster.sickness[day_index + 1:]
                )
                # user_roster.save()

            else:
                recalculate = True
                day_off_call_in_index = day_index
                break

        if recalculate:
            break

        sickness_length -= sickness_claim_in_week
        weeks_calculated += 1
        first_pos = 0
        sickness_claim_in_week = min(sickness_length, 7)
        last_pos = min(7, sickness_claim_in_week)
        week_number += 1

    if recalculate:
        day_index = day_off_call_in_index
        user_roster = Roster.objects.get(owner=user, week_number=week_number)

        rosters = get_rosters_by_week(week_number)
        rosters_with_day_off = [
            roster
            for roster in rosters
            if roster.off_days[day_index] == "1"
        ]

        users_for_day_off_call_in = [
            roster.owner
            for roster in rosters_with_day_off
        ]

        day_off_user = random.choice(users_for_day_off_call_in)
        day_off_user_roster = Roster.objects.get(owner=day_off_user, week_number=week_number)

        day_off_user_roster.off_days = (
            day_off_user_roster.off_days[:day_index] +
            CHAR_ZERO +
            day_off_user_roster.off_days[day_index + 1:]
            )
        day_off_user_roster.day_off_call_in_days = (
            day_off_user_roster.day_off_call_in_days[:day_index] +
            CHAR_ONE +
            day_off_user_roster.day_off_call_in_days[day_index + 1:]
            )
        day_off_user_roster.schedule = (
            day_off_user_roster.schedule[:day_index * 3 + shift_index] +
            CHAR_ONE +
            day_off_user_roster.schedule[day_index * 3 + shift_index + 1:]
            )
        # day_off_user_roster.save()

        user_roster.schedule = (
            user_roster.schedule[:day_index * 3 + shift_index] +
            CHAR_ZERO +
            user_roster.schedule[day_index * 3 + shift_index + 1:])
        user_roster.sickness = (
            user_roster.sickness[:day_index] +
            CHAR_ONE +
            user_roster.sickness[day_index + 1:]
        )
        # user_roster.save()

        for roster in rosters:
            if contains_character_from_index(roster.reserve_call_in_days, day_index + 1, "1"):
                roster.reserve_call_in_days = roster.reserve_call_in_days[:day_index + 1] + CHAR_ZERO * (
                    len(roster.reserve_call_in_days) - day_index - 1)
                roster.reserve_call_in = False

            if contains_character_from_index(roster.day_off_call_in_days, day_index + 1, "1"):
                roster.day_off_call_in_days = roster.day_off_call_in_days[:day_index + 1] + CHAR_ZERO * (
                    len(roster.day_off_call_in_days) - day_index - 1)
                roster.day_off_call_in = False

            # roster.save()

        day_index = 7 * (week_number - get_current_week_number(0)) + day_index

        reoptimize_schedule_after_sickness(15, 1, day_index + 1)

    # sickness for application week
    if end_date > first_day_for_application_week:
        remaining_sick_claim = min(sickness_length + 1, (end_date - first_day_for_application_week).days + 1)

        application_week_number = get_current_week_number(2)
        user_roster = get_roster_by_user_and_week_number(
            user, application_week_number)

        if start_date > first_day_for_application_week:
            first_pos = sickness_first_day_of_week - 1
        else:
            first_pos = 0

        if remaining_sick_claim > 7:
            last_pos = 7
        else:
            last_pos = remaining_sick_claim

        user_roster.sickness = replace_string_from_to_with_char(
            user_roster.sickness, first_pos, last_pos, CHAR_ONE)
        user_roster.vacation = replace_string_from_to_with_char(
            user_roster.sickness, first_pos, last_pos, CHAR_ZERO)
        user_roster.application = replace_string_from_to_with_char(
            user_roster.application, first_pos * 3, last_pos * 3, CHAR_ZERO)
        user_roster.save()

        remaining_sick_claim -= DAYS_IN_WEEK

        while remaining_sick_claim > 0:
            application_week_number += 1
            user_roster = get_roster_by_user_and_week_number(user, week_number)

            if remaining_sick_claim > 7:
                user_roster.sickness = replace_string_from_to_with_char(
                    user_roster.sickness, 0, 7, CHAR_ONE)
                user_roster.vacation = replace_string_from_to_with_char(
                    user_roster.sickness, 0, 7, CHAR_ZERO)
            else:
                user_roster.sickness= replace_string_from_to_with_char(
                    user_roster.sickness, 0, remaining_sick_claim, CHAR_ONE)
                user_roster.sickness = replace_string_from_to_with_char(
                    user_roster.sickness, 0, remaining_sick_claim, CHAR_ZERO)

            user_roster.save()
            remaining_sick_claim -= DAYS_IN_WEEK

    msg = get_sickness_claim_msg(start_date, end_date)
    return msg
