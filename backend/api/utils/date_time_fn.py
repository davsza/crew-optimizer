from datetime import date, datetime, timedelta
from typing import Tuple


def current_dt() -> datetime:
    """
    Get the current date and time.

    Returns:
        datetime: The current local date and time.
    """
    return datetime.now()


def get_current_week_number(additional_week: int) -> int:
    """
    Calculate the week number for the current date, with an optional adjustment.

    Args:
        additional_week (int): Number of weeks to add to the current week.

    Returns:
        int: The adjusted week number.
    """
    today = current_dt()
    iso_calendar = today.isocalendar()
    current_week_number = iso_calendar[1] 
    return current_week_number + additional_week


def current_year() -> int:
    """
    Get the current year based on today's date.

    This function retrieves the current year from the system date.

    Returns:
        int: The current year as an integer.
    """
    today = current_dt()
    
    return today.year


def get_first_and_last_day_of_week(year: int, week: int) -> Tuple[date, date]:
    """
    Get the first and last days of a given week in a specific year.

    This function calculates the first and last day of a specified week number within
    the given year. The first day of the week is considered Monday, and the week number
    is based on the ISO calendar system.

    Args:
        year (int): The year to calculate the week dates for.
        week (int): The week number (1-52 or 1-53) for which the first and last days are needed.

    Returns:
        Tuple[date, date]: A tuple containing the first and last day of the given week as `date` objects.
    """
    first_day_of_year = datetime(year, 1, 1)
    first_monday = first_day_of_year + timedelta(days=(7 - first_day_of_year.weekday()) % 7)
    first_day = first_monday + timedelta(weeks=week - 1)
    last_day = first_day + timedelta(days=6)
    return first_day.date(), last_day.date()