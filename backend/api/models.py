from django.db import models
from django.contrib.auth.models import User
from .utils.constants import DAYS_IN_WEEK, NUMBER_OF_SHIFTS, MESSAGE_MAX_LENGTH


class Roster(models.Model):
    """
    Represents a roster of shifts for a user for a specific week and year.

    Attributes:
        week_number (int): The week number of the year (1-52 or 1-53).
        year (int): The year for which the roster is created.
        application (str): A string representing shift applications.
        schedule (str): A string representing the assigned shifts.
        modification (str): A string representing any modifications to the schedule.
        work_days (str): A string indicating which days the user is scheduled to work (length = DAYS_IN_WEEK).
        off_days (str): A string indicating which days the user has off (length = DAYS_IN_WEEK).
        reserve_days (str): A string indicating which days the user is on reserve (length = DAYS_IN_WEEK).
        reserve_call_in_days (str): A string indicating which days the user is on call for reserve shifts.
        vacation (str): A string indicating which days the user is on vacation.
        sickness (str): A string indicating which days the user is on sick leave.
        published (bool): A boolean indicating if the roster has been published.
        reserve_call_in (bool): A boolean indicating if the user is on call for reserve shifts.
        owner (User): The user associated with the roster (foreign key to the User model).

    Methods:
        __str__() -> str:
            Returns a string representation of the Roster, typically including the week number and year.
    """
    
    week_number: int
    year: int
    application: str
    schedule: str
    modification: str
    work_days: str
    off_days: str
    reserve_days: str
    reserve_call_in_days: str
    vacation: str
    sickness: str
    published: bool
    reserve_call_in: bool
    owner: models.ForeignKey

    week_number = models.IntegerField()
    year = models.IntegerField()
    application = models.CharField(max_length=NUMBER_OF_SHIFTS)
    schedule = models.CharField(max_length=NUMBER_OF_SHIFTS)
    modification = models.CharField(max_length=NUMBER_OF_SHIFTS)
    work_days = models.CharField(max_length=DAYS_IN_WEEK)
    off_days = models.CharField(max_length=DAYS_IN_WEEK)
    reserve_days = models.CharField(max_length=DAYS_IN_WEEK)
    reserve_call_in_days = models.CharField(max_length=DAYS_IN_WEEK)
    vacation = models.CharField(max_length=DAYS_IN_WEEK)
    sickness = models.CharField(max_length=DAYS_IN_WEEK)
    published = models.BooleanField(default=False)
    reserve_call_in = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shifts")

    def __str__(self) -> str:
        """
        Returns a string representation of the roster.

        The string will typically include the week number and year, e.g., 'Week 34, 2024'.
        """
        return f"Week {self.week_number}, {self.year}"


class Message(models.Model):
    """
    Represents a message sent or received by a user.

    Attributes:
        text (str): The content of the message.
        date (datetime): The date and time when the message was created.
        sent_by_user (bool): Indicates whether the message was sent by a user or not.
        owner (User): The user associated with the message.

    Methods:
        __str__() -> str:
            Returns a string representation of the message, typically the first 50 characters of the text.
    """
    text: str
    date: models.DateTimeField
    sent_by_user: bool
    owner: models.ForeignKey

    text = models.CharField(max_length=MESSAGE_MAX_LENGTH)
    date = models.DateTimeField(auto_now_add=True)
    sent_by_user = models.BooleanField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")

    def __str__(self) -> str:
        """
        Returns a string representation of the message.

        The string will contain the first 50 characters of the message text.
        """
        return self.text[:50]
