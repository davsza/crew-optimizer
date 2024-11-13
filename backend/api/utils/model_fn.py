from django.contrib.auth.models import Group, User
from django.db.models.query import QuerySet

from api.models import Message, Roster
from .date_time_fn import get_current_week
from .common_fn import is_uniform_with_char
from .constants import CHAR_ZERO

from typing import Optional, Tuple, Union



def get_supervisor_group() -> Group:
    """
    Retrieve the 'Supervisor' group from the database.

    Returns:
        Group: The Group object with the name 'Supervisor'.

    Raises:
        Group.DoesNotExist: If no group with the name 'Supervisor' exists.
    """
    return Group.objects.get(name='Supervisor')


def get_admin_users() -> QuerySet[User]:
    """
    Retrieve all users who are members of the 'Supervisor' group.

    Returns:
        QuerySet[User]: A queryset of User objects who belong to the 'Supervisor' group.
    """
    group = get_supervisor_group()
    return User.objects.filter(groups=group)


def is_user_in_group(user: User, group_name: str) -> bool:
    """
    Check if a user is a member of a specific group.

    Args:
        user (User): The user to check.
        group_name (str): The name of the group to check.

    Returns:
        bool: True if the user is in the specified group, otherwise False.
    """
    return user.groups.filter(name=group_name).exists()


def get_rosters_by_week(week_number: int, first_n: int = 15) -> QuerySet['Roster']:
    """
    Retrieve a limited number of rosters for a specified week, excluding those owned by admin users.

    Args:
        week_number (int): The ISO week number to filter the rosters by.
        first_n (int, optional): The maximum number of rosters to return. Defaults to 15.

    Returns:
        QuerySet[Roster]: A queryset of Roster objects filtered by the specified week number,
                          excluding those owned by admin users, limited to 'first_n' results.
    """
    admin_users = get_admin_users()
    rosters = Roster.objects.exclude(owner__in=admin_users).filter(week_number=week_number)
    return rosters[:first_n]



def get_past_messages_by_user(user: User) -> QuerySet['Message']:
    """
    Retrieve all past messages for a specific user.

    Args:
        user (User): The user whose messages are to be retrieved.

    Returns:
        QuerySet[Message]: A queryset of Message objects owned by the specified user.
    """
    messages = Message.objects.filter(owner=user)
    return messages


def get_roster_by_user_and_week_number(user: User, week_number: int) -> Optional[Roster]:
    """
    Retrieve the roster for a given user and week number.

    This function queries the database to get the roster associated with a specific user
    and a specific week number. If no roster is found, it returns None.

    Args:
        user: The user whose roster is to be fetched.
        week_number (int): The week number for which the roster is required.

    Returns:
        Optional[Roster]: The roster object if found, or None if no roster exists for the user and week number.
    """
    try:
        roster = Roster.objects.get(owner=user, week_number=week_number)
        return roster
    except Roster.DoesNotExist:
        return None
    
    
def get_users_without_application() -> Tuple[bool, Union[str, None]]:
    """
    Retrieve the users who do not have any application for the current week.

    This function identifies users who are not part of the 'Supervisor' group and checks their roster 
    for the current week (with a 2-week offset). If a user has no application (represented by '0' 
    in the roster string), they are added to the list.

    Returns:
        Tuple[bool, Union[str, None]]: A tuple where the first element is a boolean indicating
        whether any users without applications were found, and the second element is either a
        warning message with the list of users or None if no users are found.
    """
    supervisor_group = Group.objects.get(name='Supervisor')
    users = User.objects.exclude(groups=supervisor_group)
    user_list = []

    week_number = get_current_week(2)

    for user in users:
        try:
            roster = Roster.objects.get(owner=user, week_number=week_number)
            application = roster.application

            if is_uniform_with_char(application, CHAR_ZERO):
                user_list.append(user.username)

        except Roster.DoesNotExist:
            continue

    if user_list:
        return (True, f"Warning! The following users don't have any application: {', '.join(user_list)}" if len(user_list) > 1 else f"The following user doesn't have any application: {user_list[0]}")
    else:
        return (False,)
    
    
def is_user_in_group(user: User, group_name: str) -> bool:
    """
    Check if a user belongs to a specific group.

    This function checks whether the given user is a member of the group specified
    by the `group_name` parameter.

    Args:
        user (User): The user to check.
        group_name (str): The name of the group to check membership against.

    Returns:
        bool: True if the user is a member of the specified group, False otherwise.
    """
    return user.groups.filter(name=group_name).exists()