import datetime
from .models import Shift
from django.contrib.auth.models import User, Group
from django.db.models.query import QuerySet


def get_current_week(additional_week: int) -> int:
    current_date = datetime.datetime.now()
    iso_calendar = current_date.isocalendar()
    current_week_number = iso_calendar[1]
    return current_week_number + additional_week


def get_supervisor_group() -> Group:
    return Group.objects.get(name='Supervisor')


def get_admin_users() -> QuerySet[User]:
    group = get_supervisor_group()
    return User.objects.filter(groups=group)


def get_shifts_by_week(week_number: int) -> QuerySet[Shift]:
    admin_users = get_admin_users()
    shifts = Shift.objects.exclude(
        owner__in=admin_users).filter(week=week_number)
    return shifts
