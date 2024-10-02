import datetime
from django.contrib.auth.models import User, Group
from api.models import Message, Shift
from django.db.models.query import QuerySet
import json


def get_current_week(additional_week: int) -> int:
    current_date = datetime.datetime.now()
    iso_calendar = current_date.isocalendar()
    current_week_number = iso_calendar[1]
    return current_week_number + additional_week


def is_weekend() -> bool:
    today = datetime.datetime.now()
    return today.weekday() >= 5


def get_supervisor_group() -> Group:
    return Group.objects.get(name='Supervisor')


def get_admin_users() -> QuerySet[User]:
    group = get_supervisor_group()
    return User.objects.filter(groups=group)


def user_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()


def get_shifts_by_week(week_number: int) -> QuerySet[Shift]:
    admin_users = get_admin_users()
    shifts = Shift.objects.exclude(
        owner__in=admin_users).filter(week=week_number)
    return shifts


def get_past_messages(user):
    messages = Message.objects.filter(owner=user)
    return messages


def is_empty_application_string(application_string, empty_character):
    return all(char == empty_character for char in application_string)


def get_default_application_string(empty_character):
    return empty_character * 21


def convert_string_to_json(application_string):
    days = ["monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"]
    schedule = {}
    for i, day in enumerate(days):
        start_index = i * 3
        schedule[day] = {
            "morning": True if application_string[start_index] == "1" else (None if application_string[start_index] == "x" else False),
            "afternoon": True if application_string[start_index + 1] == "1" else (None if application_string[start_index + 1] == "x" else False),
            "night": True if application_string[start_index + 2] == "1" else (None if application_string[start_index + 2] == "x" else False)
        }

    return json.dumps({"shift": schedule}, indent=4)


def convert_json_to_string(shift_json, parse_none_as_x=False):
    days = ["monday", "tuesday", "wednesday",
            "thursday", "friday", "saturday", "sunday"]
    values_string = ""

    for day in days:
        shifts = shift_json["shift"].get(day, {})
        for shift in ['morning', 'afternoon', 'night']:
            value = shifts.get(shift, None)
            if parse_none_as_x and value is None:
                values_string += "x"
            else:
                values_string += str(int(bool(value)))

    return values_string


def get_summary(application, current_modification=None, full_modification=None):
    def format_application_day(day, shifts):
        active_shifts = [shift_name for shift_name,
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
        inactive_shifts = [shift_name for shift_name,
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

    if not current_modification and not full_modification:
        application_summary_result = []
        for day, shifts in application['shift'].items():
            day_summary = format_application_day(day, shifts)
            if day_summary:
                application_summary_result.append(day_summary)

        ret_val = "Your application includes shifts on the following days and times: " + \
            ', '.join(application_summary_result) + \
            ". Would you like to modify it?"
    else:
        full_modification_application_summary_result = []
        full_modification_cancellation_summary_result = []
        for day, shifts in full_modification['shift'].items():
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

        if current_modification:
            for day, shifts in current_modification['shift'].items():
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


def order_json_by_days(shift_json):
    days_of_week = ["monday", "tuesday", "wednesday",
                    "thursday", "friday", "saturday", "sunday"]
    ordered_json = {day: shift_json[day]
                    for day in days_of_week if day in shift_json}
    return ordered_json


def get_shift(user, week):
    shift = Shift.objects.get(owner=user, week=week)
    return shift


def complement_shifts(input_json_raw):
    days_of_week = ["monday", "tuesday", "wednesday",
                    "thursday", "friday", "saturday", "sunday"]
    default_shifts = {"morning": None, "afternoon": None, "night": None}

    input_json = json.loads(input_json_raw)

    current_shifts = input_json.get("shift", {})

    for day in days_of_week:
        if day in current_shifts:  # monday, tuesday, etc...
            for shift in default_shifts:
                if shift not in current_shifts[day]:
                    current_shifts[day][shift] = default_shifts[shift]
            # day = {shift: day[shift]
            #         for shift in shifts_of_the_day if shift in day}
        else:
            current_shifts[day] = default_shifts.copy()

    input_json["shift"] = current_shifts
    return input_json


def overwrite_binary(str1, str2):
    if len(str1) != len(str2):
        raise ValueError("Both strings must be of the same length")

    application_summary_result = ""
    for i in range(len(str1)):
        if str1[i] == '0' or str1[i] == '1':
            application_summary_result += str1[i]
        else:
            application_summary_result += str2[i]

    return application_summary_result


def get_users_without_application():
    supervisor_group = Group.objects.get(name='Supervisor')
    users = User.objects.exclude(groups=supervisor_group)
    user_list = []
    week_number = get_current_week(2)
    for user in users:
        shift = Shift.objects.get(owner=user, week=week_number)
        application = shift.applied_shift
        if is_empty_application_string(application, '0'):
            user_list.append(user.username)
    return (True, (f"Warning! The following users don't have any application: {', '.join(user_list)}" if len(user_list) > 1 else f"The following user doesn't have any application: {user_list[0]}")) if user_list else (False,)


def user_in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()
