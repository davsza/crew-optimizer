from typing import Dict, Optional
from datetime import datetime


def get_summary(
    roster_json: Dict,
    current_modification_json: Optional[Dict] = None,
    full_modification_json: Optional[Dict] = None
) -> str:
    """
    Generate a summary of shift applications and cancellations.

    This function takes a roster JSON, along with optional modification JSONs, 
    and returns a summary of shifts applied for, canceled, or ongoing.

    Args:
        roster_json (dict): The original roster JSON containing shift details.
        current_modification_json (dict, optional): The current modification JSON containing
                                                    applied shifts and cancellations.
        full_modification_json (dict, optional): The full modification JSON containing all ongoing
                                                 changes.

    Returns:
        str: A summary message of applications and cancellations.
    """

    def format_application_day(day: str, shifts: Dict[str, bool]) -> Optional[str]:
        """
        Format the shift application summary for a specific day.
        
        Args:
            day (str): The day of the week.
            shifts (dict): A dictionary with shift times (morning, afternoon, night) as keys and
                           boolean values.

        Returns:
            str or None: A formatted string summarizing the applied shifts for the day, or None i
                         no shifts are applied.
        """
        active_shifts = [shift for shift, active in shifts.items() if active]

        if not active_shifts:
            return None

        if len(active_shifts) == 3:
            return f"{day.capitalize()} morning, afternoon, and night"
        if len(active_shifts) == 2:
            return f"{day.capitalize()} {active_shifts[0]} and {active_shifts[1]}"
        return f"{day.capitalize()} {active_shifts[0]}"

    def format_cancellation_day(day: str, shifts: Dict[str, bool]) -> Optional[str]:
        """
        Format the shift cancellation summary for a specific day.
        
        Args:
            day (str): The day of the week.
            shifts (dict): A dictionary with shift times (morning, afternoon, night) as keys and
                           boolean values indicating cancellation.

        Returns:
            str or None: A formatted string summarizing the canceled shifts for the day, or None
                         if no shifts are canceled.
        """
        inactive_shifts = [shift for shift, active in shifts.items() if active is False]

        if not inactive_shifts:
            return None

        if len(inactive_shifts) == 3:
            return f"{day.capitalize()} morning, afternoon, and night"
        if len(inactive_shifts) == 2:
            return f"{day.capitalize()} {inactive_shifts[0]} and {inactive_shifts[1]}"
        
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

            if (
                current_modification_application_summary_result and
                current_modification_cancellation_summary_result
            ):
                ret_val = (
                    "You have applied for: " +
                    ', '.join(current_modification_application_summary_result) +
                    "; and cancelled: " +
                    ', '.join(current_modification_cancellation_summary_result) +
                    ". With that, your ongoing applications are " +
                    ', '.join(full_modification_application_summary_result) +
                    "; and cancellations are " +
                    ', '.join(full_modification_cancellation_summary_result) +
                    ". Would you like to modify it any further, or save them?"
                )

            elif current_modification_application_summary_result:
                ret_val = (
                    "You have applied for: " +
                    ', '.join(current_modification_application_summary_result) +
                    ". With that, your ongoing applications are: " +
                    ', '.join(full_modification_application_summary_result)
                )

                if full_modification_cancellation_summary_result:
                    ret_val += (
                        "; and cancellations are: " +
                        ', '.join(full_modification_cancellation_summary_result)
                    )

                ret_val += (
                    ". Would you like to modify it any further, or save them?"
                )

            elif current_modification_cancellation_summary_result:
                ret_val = (
                    "You have canceled for: " +
                    ', '.join(current_modification_cancellation_summary_result) +
                    ". With that, your ongoing "
                )

                if full_modification_application_summary_result:
                    ret_val += (
                        "applications are: " +
                        ', '.join(full_modification_application_summary_result) +
                        "; and "
                    )

                ret_val += (
                    "cancellations are: " +
                    ', '.join(full_modification_cancellation_summary_result) +
                    ". Would you like to modify it any further, or save them?"
                )

        else:
            if full_modification_application_summary_result:
                ret_val = (
                    "Your ongoing applications are: " +
                    ', '.join(full_modification_application_summary_result)
                )

                if full_modification_cancellation_summary_result:
                    ret_val += (
                        "; and cancellations are: " +
                        ', '.join(full_modification_cancellation_summary_result) +
                        ". Would you like to modify it any further, or save them?"
                    )

            elif full_modification_cancellation_summary_result:
                ret_val = (
                    "Your ongoing cancellations are: " +
                    ', '.join(full_modification_cancellation_summary_result) +
                    ". Would you like to modify it any further, or save them?"
                )

            else:
                ret_val = (
                    "You don't have any ongoing modifications. " +
                    "If you'd like to change anything, please let me know!"
                )

    return ret_val


def get_vacation_and_sickess_claim_dates_wrong_warning_msg(
    mode: str,
    first_day_of_application_week: datetime,
    first_day_of_current_week: datetime,
    last_day_of_current_week: datetime
) -> str:
    """
    Generates a warning message regarding incorrect application dates for vacation or sickness.

    This function creates a warning message for the user indicating the earliest possible 
    application date for vacation or sickness claims. The message will be different based on 
    the `mode` ("vacation" or "sickness"). For sickness claims, the latest possible claim date 
    is also included.

    Args:
        mode (str): The type of claim, either "vacation" or "sickness".
        first_day_of_application_week (datetime): The first day of the application week.
        first_day_of_current_week (datetime): The first day of the current week.
        last_day_of_current_week (datetime): The last day of the current week.

    Returns:
        str: A formatted warning message.
    """
    first_date = first_day_of_application_week if mode == "vacation" else first_day_of_current_week
    msg = f"Please only apply for {mode} starting earliest {first_date.strftime('%d %B %Y')}"

    if mode == "sickness":
        msg += f" and latest {last_day_of_current_week.strftime('%d %B %Y')}"

    return msg


def get_too_much_claimed_vacation_warning_msg(
    vacation_length: int,
    maximum_vacation_claim_per_year: int,
    claimed_vacation: int
) -> str:
    """
    Generates a warning message when a user tries to claim more vacation days than they are allowed.

    This function calculates the remaining vacation days a user can claim and generates a warning
    message if the requested vacation length exceeds the allowed limit for the year.

    Args:
        vacation_length (int): The number of vacation days the user is trying to claim.
        maximum_vacation_claim_per_year (int): The maximum number of vacation days the user can
                                               claim in a year.
        claimed_vacation (int): The number of vacation days the user has already claimed in theű
                                current year.

    Returns:
        str: A formatted warning message indicating how many vacation days the user can still claim.
    """
    remaining_vacation_days = maximum_vacation_claim_per_year - claimed_vacation
    return (
        f"You can't take {vacation_length} more vacation days, "
        f"you have only {remaining_vacation_days} days left!"
    )

def get_vacation_claim_msg(
    claim: bool,
    start_date: datetime,
    end_date: datetime
) -> str:
    """
    Generates a message indicating whether a vacation claim has been applied or canceled.

    This function returns a formatted message indicating whether a vacation has been applied 
    or canceled, along with the start and end dates of the vacation.

    Args:
        claim (bool): A boolean indicating whether the vacation is being applied (True)
                      or canceled (False).
        start_date (datetime): The start date of the vacation.
        end_date (datetime): The end date of the vacation.

    Returns:
        str: A formatted message indicating the vacation status (applied or canceled) along
             with the dates.
    """
    return (
        f"You have {'applied' if claim else 'canceled'} vacation "
        f"from {start_date.strftime('%d %b')} to {end_date.strftime('%d %b')}"
    )

def get_vacation_claim_rejection_by_admin_msg(
    username: str,
    start_date: datetime,
    end_date: datetime
) -> str:
    """
    Generates a message indicating that a vacation claim has been successfully rejected
    by the admin.

    This function returns a formatted message stating that a vacation claim has been rejected for a 
    specific user, along with the start and end dates of the vacation.

    Args:
        username (str): The username of the user whose vacation claim is being rejected.
        start_date (datetime): The start date of the vacation.
        end_date (datetime): The end date of the vacation.

    Returns:
        str: A formatted message indicating that the vacation claim has been rejected, including
             the dates.
    """
    return (
        f"Vacation claim is successfully rejected for {username} "
        f"from {start_date.strftime('%d %b')} to {end_date.strftime('%d %b')}"
    )

def get_sickness_claim_msg(
    start_date: datetime,
    end_date: datetime
) -> str:
    """
    Generates a message indicating that a sickness claim has been applied.

    This function returns a formatted message stating that a sickness claim has been applied, 
    along with the start and end dates of the sickness period.

    Args:
        start_date (datetime): The start date of the sickness claim.
        end_date (datetime): The end date of the sickness claim.

    Returns:
        str: A formatted message indicating that the sickness claim has been applied, including
             the dates.
    """
    return (
        f"You have applied sickness from {start_date.strftime('%d %b')}"
        f" to {end_date.strftime('%d %b')}"
    )
    