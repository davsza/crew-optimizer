import datetime


def get_current_week():
    current_date = datetime.datetime.now()
    iso_calendar = current_date.isocalendar()
    current_week_number = iso_calendar[1]
    return current_week_number
