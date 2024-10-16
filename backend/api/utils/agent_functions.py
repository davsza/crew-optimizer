import json
from datetime import datetime, timedelta
from django.contrib.auth.models import Group, User
from django.db.models.query import QuerySet
from api.models import Message, Roster
from .constants import CHAR_ONE, CHAR_ZERO, DAYS_IN_WEEK


def now():
    return datetime.now()


def get_current_week(additional_week: int) -> int:
    today = now()
    iso_calendar = today.isocalendar()
    current_week_number = iso_calendar[1]
    return current_week_number + additional_week


def is_weekend() -> bool:
    today = now()
    return today.weekday() >= 5


def get_supervisor_group() -> Group:
    return Group.objects.get(name='Supervisor')


def get_admin_users() -> QuerySet[User]:
    group = get_supervisor_group()
    return User.objects.filter(groups=group)


def user_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


def get_rosters_by_week(week_number: int) -> QuerySet[Roster]:
    admin_users = get_admin_users()
    rosters = Roster.objects.exclude(
        owner__in=admin_users).filter(week_number=week_number)
    return rosters


def get_past_messages(user):
    messages = Message.objects.filter(owner=user)
    return messages


def is_empty_binary_roster(binary_roster, empty_character):
    return all(char == empty_character for char in binary_roster)


def get_default_binary_roster(empty_character):
    return empty_character * 21


def convert_string_to_json(binary_roster):
    days = ["monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"]
    ret_json = {}
    for i, day in enumerate(days):
        start_index = i * 3
        ret_json[day] = {
            "morning": True if binary_roster[start_index] == "1" else (None if binary_roster[start_index] == "x" else False),
            "afternoon": True if binary_roster[start_index + 1] == "1" else (None if binary_roster[start_index + 1] == "x" else False),
            "night": True if binary_roster[start_index + 2] == "1" else (None if binary_roster[start_index + 2] == "x" else False)
        }

    return json.dumps({"roster": ret_json}, indent=4)


def convert_json_to_string(roster_json, parse_none_as_x=False):
    days = ["monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"]
    values_string = ""

    for day in days:
        roster = roster_json["roster"].get(day, {})
        for shift in ['morning', 'afternoon', 'night']:
            value = roster.get(shift, None)
            if parse_none_as_x and value is None:
                values_string += "x"
            else:
                values_string += str(int(bool(value)))

    return values_string


def get_summary(roster_json, current_modification_json=None, full_modification_json=None):
    def format_application_day(day, shifts):
        active_shifts = [shift for shift,
                         active in shifts.items() if active]

        if not active_shifts:
            return None

        if len(active_shifts) == 3:
            return f"{day.capitalize()} morning, afternoon, and night"
        elif len(active_shifts) == 2:
            return f"{day.capitalize()} {active_shifts[0]} and {active_shifts[1]}"
        else:
            return f"{day.capitalize()} {active_shifts[0]}"

    def format_cancellation_day(day, shifts):
        inactive_shifts = [shift for shift,
                           active in shifts.items() if active is False]

        if not inactive_shifts:
            return None

        if len(inactive_shifts) == 3:
            return f"{day.capitalize()} morning, afternoon, and night"
        elif len(inactive_shifts) == 2:
            return f"{day.capitalize()} {inactive_shifts[0]} and {inactive_shifts[1]}"
        else:
            return f"{day.capitalize()} {inactive_shifts[0]}"

    ret_val = ""

    if not current_modification_json and not full_modification_json:
        application_summary_result = []
        for day, shifts in roster_json['roster'].items():
            day_summary = format_application_day(day, shifts)
            if day_summary:
                application_summary_result.append(day_summary)

        ret_val = "Your application includes shifts on the following days and times: " + \
            ', '.join(application_summary_result) + \
            ". Would you like to modify it?"
    else:
        full_modification_application_summary_result = []
        full_modification_cancellation_summary_result = []
        for day, shifts in full_modification_json['roster'].items():
            day_application_summary = format_application_day(day, shifts)
            day_cancellation_summary = format_cancellation_day(day, shifts)
            if day_application_summary:
                full_modification_application_summary_result.append(
                    day_application_summary)
            if day_cancellation_summary:
                full_modification_cancellation_summary_result.append(
                    day_cancellation_summary)

        current_modification_application_summary_result = []
        current_modification_cancellation_summary_result = []

        if current_modification_json:
            for day, shifts in current_modification_json['roster'].items():
                day_application_summary = format_application_day(day, shifts)
                day_cancellation_summary = format_cancellation_day(day, shifts)
                if day_application_summary:
                    current_modification_application_summary_result.append(
                        day_application_summary)
                if day_cancellation_summary:
                    current_modification_cancellation_summary_result.append(
                        day_cancellation_summary)

            if current_modification_application_summary_result and current_modification_cancellation_summary_result:
                ret_val = "You have applied for: " + ', '.join(current_modification_application_summary_result) + "; and cancelled: " + ', '.join(current_modification_cancellation_summary_result) + ". With that, your ongoing applications are " + ', '.join(
                    full_modification_application_summary_result) + "; and cancellations are " + ', '.join(full_modification_cancellation_summary_result) + ". Would you like to modify it any further, or save them?"
            elif current_modification_application_summary_result:
                ret_val = "You have applied for: " + ', '.join(current_modification_application_summary_result) + \
                    ". With that, your ongoing applications are: " + \
                    ', '.join(full_modification_application_summary_result)
                if full_modification_cancellation_summary_result:
                    ret_val += "; and cancellations are: " + \
                        ', '.join(
                            full_modification_cancellation_summary_result)
                ret_val += ". Would you like to modify it any further, or save them?"
            elif current_modification_cancellation_summary_result:
                ret_val = "You have canceled for: " + \
                    ', '.join(current_modification_cancellation_summary_result) + \
                    ". With that, your ongoing "
                if full_modification_application_summary_result:
                    ret_val += "applications are: " + \
                        ', '.join(
                            full_modification_application_summary_result) + "; and "
                ret_val += "cancellations are: " + \
                    ', '.join(full_modification_cancellation_summary_result) + \
                    ". Would you like to modify it any further, or save them?"
        else:
            if full_modification_application_summary_result:
                ret_val = "Your ongoing applications are: " + ', '.join(
                    full_modification_application_summary_result)
                if full_modification_cancellation_summary_result:
                    ret_val += "; and cancellations are: " + \
                        ', '.join(
                            full_modification_cancellation_summary_result) + ". Would you like to modify it any further, or save them?"
            elif full_modification_cancellation_summary_result:
                ret_val = "Your ongoing cancellations are: " + ', '.join(
                    full_modification_cancellation_summary_result) + ". Would you like to modify it any further, or save them?"
            else:
                ret_val = "You don't have any ongoing modifications. If you'd like to change anything, please let me know!"

    return ret_val


def order_json_by_days(roster_json):
    days_of_week = ["monday", "tuesday", "wednesday",
                    "thursday", "friday", "saturday", "sunday"]
    ordered_json = {day: roster_json[day]
                    for day in days_of_week if day in roster_json}
    return ordered_json


def get_roster(user, week_number):
    roster = Roster.objects.get(owner=user, week_number=week_number)
    return roster


def complement_roster(input_json_raw):
    days_of_week = ["monday", "tuesday", "wednesday",
                    "thursday", "friday", "saturday", "sunday"]
    default_shifts = {"morning": None, "afternoon": None, "night": None}

    input_json = json.loads(input_json_raw)

    current_shifts = input_json.get("roster", {})

    for day in days_of_week:
        if day in current_shifts:
            for shift in default_shifts:
                if shift not in current_shifts[day]:
                    current_shifts[day][shift] = default_shifts[shift]
        else:
            current_shifts[day] = default_shifts.copy()

    input_json["roster"] = current_shifts
    return input_json


def overwrite_binary(original_binary, replace_with):
    application_summary_result = ""
    for i in range(len(original_binary)):
        if original_binary[i] == CHAR_ZERO or original_binary[i] == CHAR_ONE:
            application_summary_result += original_binary[i]
        else:
            application_summary_result += replace_with[i]

    return application_summary_result


def get_users_without_application():
    supervisor_group = Group.objects.get(name='Supervisor')
    users = User.objects.exclude(groups=supervisor_group)
    user_list = []
    week_number = get_current_week(2)
    for user in users:
        roster = Roster.objects.get(owner=user, week_number=week_number)
        application = roster.application
        if is_empty_binary_roster(application, CHAR_ZERO):
            user_list.append(user.username)
    return (True, (f"Warning! The following users don't have any application: {', '.join(user_list)}" if len(user_list) > 1 else f"The following user doesn't have any application: {user_list[0]}")) if user_list else (False,)


def user_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


def get_dates_from_vacation_json(json_input):
    data = json.loads(json_input)
    vacation = data['vacation']
    today = now()
    start_date = datetime.strptime(
        vacation['start'], '%d-%m').replace(year=today.year).date()
    end_date = datetime.strptime(
        vacation['end'], '%d-%m').replace(year=today.year).date()
    if 'save' in vacation:
        save = vacation['save']
        user = None
    else:
        save = False
        user = User.objects.get(username=vacation["user"])
    return start_date, end_date, save, user


def first_day_of_week(year, week):
    first_day_of_year = datetime(year, 1, 1)
    first_monday = first_day_of_year + \
        timedelta(days=(7 - first_day_of_year.weekday()) % 7)
    first_day = first_monday + timedelta(weeks=week - 1)
    return first_day.date()


def current_year():
    today = now()
    return today.year


def get_claimed_vacation(user, year):
    rosters = Roster.objects.filter(owner=user, year=year)
    return sum(str(roster.vacation).count(CHAR_ONE) for roster in rosters)


def replace_binary(binary_to_replace, from_pos, to_pos, character):

    replaced_binary = (
        binary_to_replace[:from_pos] +
        character * (to_pos - from_pos) +
        binary_to_replace[to_pos:]
    )

    return replaced_binary


def save_vacation_claim(user, vacation_week_number, vacation_first_day_of_week, vacation_length, replacing_character):
    week_number = vacation_week_number
    vac_claim_days = vacation_length
    roster = get_roster(user, week_number)
    vac_claim_in_week = DAYS_IN_WEEK - vacation_first_day_of_week + 1

    first_pos = vacation_first_day_of_week - 1
    if vacation_first_day_of_week + vacation_length - 1 > 7:
        last_pos = 7
    else:
        last_pos = vacation_first_day_of_week + vacation_length - 1

    roster.vacation = replace_binary(
        roster.vacation, first_pos, last_pos,  replacing_character)
    if replacing_character == CHAR_ONE:
        roster.application = replace_binary(
            roster.application, first_pos * 3, last_pos * 3, CHAR_ZERO)
    roster.save()
    vac_claim_days -= vac_claim_in_week

    while vac_claim_days > 0:
        roster = get_roster(user, week_number + 1)
        if vac_claim_days > 7:
            roster.vacation = replace_binary(
                roster.vacation, 0, 7, replacing_character)
        else:
            roster.vacation = replace_binary(
                roster.vacation, 0, vac_claim_days, replacing_character)
        vac_claim_days -= DAYS_IN_WEEK
        roster.save()


def get_roster_mapping(rosters, start, end, offset=0):
    return {i - offset: rosters[i - start] for i in range(start, end)}


def get_day_mapping(days, start, end):
    return {i: days[i - start] for i in range(start, end)}


def late_vacation_warning_msg(first_day_for_application_week):
    return f"Please only apply for vacation starting earliest {first_day_for_application_week.strftime('%d %B %Y')}"


def too_much_claimed_vacation_warning_msg(vacation_length, maximum_vacation_claim_per_year, claimed_vacation):
    return f"You can't take {vacation_length} more vacations days, you have only {maximum_vacation_claim_per_year - claimed_vacation} days left!"


def vacation_claim_msg(claim, start_date, end_date):
    return f"You have {'applied' if claim else 'calceled'} vacation from {start_date.strftime('%d %b')} to {end_date.strftime('%d %b')}"


def vacation_claim_rejection_msg(username):
    return f"Vacation claim is successfully rejected for {username}"


def max_consecutive_days(roster, character_to_find):
    max_count = 0
    current_count = 0

    for char in roster:
        if char == character_to_find:
            current_count += 1
        else:
            max_count = max(max_count, current_count)
            current_count = 0

    max_count = max(max_count, current_count)

    return max_count
