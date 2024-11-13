from django.contrib.auth.models import Group, User
from django.http import JsonResponse

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from typing import Dict, Optional

from .agent import call_agent
from .models import Message, Roster
from .serializers import MessageSerializer, RosterSerializer, UserSerializer


class RosterGivenWeekQuery(generics.ListAPIView):
    """
    This view retrieves the roster for a given user for a specific week number. 
    It expects the week number to be passed as a URL parameter and only returns 
    results for the authenticated user.

    Attributes:
        serializer_class (RosterSerializer): The serializer used to transform the roster data.
        permission_classes (list): A list of permissions required to access the view.
    
    Methods:
        get_queryset(self) -> QuerySet:
            Returns the queryset of the rosters for the authenticated user and the specified week number.
    """

    serializer_class = RosterSerializer
    
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves the roster for the authenticated user for the given week number.

        Args:
            None

        Returns:
            QuerySet: A queryset of rosters matching the authenticated user and the week number.
        """
        user = self.request.user
        week_number = self.kwargs.get('week_number')
        return Roster.objects.filter(owner=user, week_number=week_number)


class RosterGivenWeekQueryAdmin(generics.ListAPIView):
    """
    This view retrieves the roster for a specific week number, excluding users in the 
    'Supervisor' group. It expects the week number to be passed as a URL parameter and 
    ensures that the user is authenticated.

    Attributes:
        serializer_class (RosterSerializer): The serializer used to transform the roster data.
        permission_classes (list): A list of permissions required to access the view.
    
    Methods:
        get_queryset(self) -> QuerySet:
            Returns the queryset of the rosters for the specified week number, excluding 
            the 'Supervisor' group users.
    """

    serializer_class = RosterSerializer
    
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves the roster for the specified week number, excluding users who belong 
        to the 'Supervisor' group.

        Args:
            None

        Returns:
            QuerySet: A queryset of rosters for the specified week number, excluding 
                      the 'Supervisor' group users.
        """
        week_number = self.kwargs.get('week_number')
        supervisor_group = Group.objects.get(name='Supervisor')
        return Roster.objects.filter(week_number=week_number).exclude(owner__groups=supervisor_group)


class RosterPreviousWeeksQuery(generics.ListAPIView):
    """
    This view retrieves all the rosters for a user in the weeks prior to or including 
    the given week number. The user is authenticated before accessing the view.

    Attributes:
        serializer_class (RosterSerializer): The serializer used to transform the roster data.
        permission_classes (list): A list of permissions required to access the view.
    
    Methods:
        get_queryset(self) -> QuerySet:
            Returns the queryset of rosters for the user where the week number is less 
            than or equal to the provided week number.
    """

    serializer_class = RosterSerializer
    
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves the roster for the specified user for weeks less than or equal 
        to the provided week number.

        Args:
            None

        Returns:
            QuerySet: A queryset of rosters for the user for the specified week and all previous weeks.
        """
        user = self.request.user
        week_number = self.kwargs.get('week_number')
        return Roster.objects.filter(owner=user, week_number__lte=week_number)


class MessageListCreate(generics.ListCreateAPIView):
    """
    This view allows listing and creating messages for the authenticated user. 
    The user can see their own messages, ordered by the most recent first, 
    and can create new messages which will be associated with their account.

    Attributes:
        serializer_class (Type[MessageSerializer]): The serializer used to convert the message data.
        permission_classes (list): A list of permissions required to access the view.

    Methods:
        get_queryset(self) -> QuerySet:
            Returns the queryset of messages for the authenticated user, ordered by ID in descending order.
        perform_create(self, serializer) -> None:
            Saves the message with the authenticated user as the owner.
    """

    serializer_class = MessageSerializer
    
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves the messages for the authenticated user, ordered by the ID in descending order.

        Args:
            None

        Returns:
            QuerySet: A queryset of messages for the authenticated user, ordered by ID in descending order.
        """
        user = self.request.user
        return Message.objects.filter(owner=user).order_by('-id')

    def perform_create(self, serializer) -> None:
        """
        Saves the new message with the authenticated user as the owner.

        Args:
            serializer (MessageSerializer): The serializer containing the validated data for the new message.

        Returns:
            None
        """
        serializer.save(owner=self.request.user)


class RosterListCreate(generics.ListCreateAPIView):
    """
    This view allows listing and creating rosters for the authenticated user. 
    The user can see their own rosters and create new ones.

    Attributes:
        serializer_class (Type[RosterSerializer]): The serializer used to convert the roster data.
        permission_classes (list): A list of permissions required to access the view.

    Methods:
        get_queryset(self) -> QuerySet:
            Returns the queryset of rosters for the authenticated user.
        perform_create(self, serializer) -> None:
            Saves the roster with the authenticated user as the owner.
    """

    serializer_class = RosterSerializer
    
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves the rosters for the authenticated user.

        Args:
            None

        Returns:
            QuerySet: A queryset of rosters for the authenticated user.
        """
        user = self.request.user
        return Roster.objects.filter(owner=user)

    def perform_create(self, serializer) -> None:
        """
        Saves the new roster with the authenticated user as the owner.

        Args:
            serializer (RosterSerializer): The serializer containing the validated data for the new roster.

        Returns:
            None
        """
        serializer.save(owner=self.request.user)


class RosterDelete(generics.DestroyAPIView):
    """
    This view allows deleting a roster for the authenticated user.
    The user can only delete their own rosters.

    Attributes:
        serializer_class (Type[RosterSerializer]): The serializer used to convert the roster data.
        permission_classes (list): A list of permissions required to access the view.

    Methods:
        get_queryset(self) -> QuerySet:
            Returns the queryset of rosters for the authenticated user, 
            which are available for deletion.
    """

    serializer_class = RosterSerializer
    
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retrieves the rosters for the authenticated user that can be deleted.

        Args:
            None

        Returns:
            QuerySet: A queryset of rosters owned by the authenticated user.
        """
        user = self.request.user
        return Roster.objects.filter(owner=user)


class CreateUserView(generics.CreateAPIView):
    """
    This view allows the creation of a new user.

    Attributes:
        queryset (QuerySet): The queryset of all User objects.
        serializer_class (Type[UserSerializer]): The serializer used for validating and creating a new user.
        permission_classes (list): The permission classes that define the access level for this view.

    Methods:
        perform_create(self, serializer):
            Saves the user instance created via the serializer.
    """

    queryset = User.objects.all()
    
    serializer_class = UserSerializer
    
    permission_classes = [AllowAny]
    
    def perform_create(self, serializer) -> None:
        """
        Creates a new user and saves the instance using the provided serializer.

        Args:
            serializer (UserSerializer): The validated serializer containing user data.

        Returns:
            None
        """
        serializer.save()


class UserDataView(APIView):
    """
    A view that returns the username and group of the authenticated user.

    If the user is authenticated, their username and group name are returned as a JSON response.
    If the user is not authenticated, an error message with a 401 status code is returned.

    Methods:
        get(self, request):
            Handles GET requests to retrieve user data (username and group).
    """

    def get(self, request) -> JsonResponse:
        """
        Handles GET requests to return the authenticated user's username and group.

        Args:
            request (HttpRequest): The HTTP request object that contains the user information.

        Returns:
            JsonResponse: A JSON response containing the username and group, or an error message.
        """
        user = request.user

        if user.is_authenticated:
            user_groups = user.groups.all()
            group_name: Optional[str] = None

            if user_groups.exists():
                group = user_groups.first()
                group_name = group.name

            return JsonResponse({'username': user.username, 'group': group_name})

        return JsonResponse({'error': 'User is not authenticated'}, status=401)


def get_user_details(request) -> JsonResponse:
    """
    Retrieves a list of users excluding those in the 'Supervisor' group.

    If the 'Supervisor' group exists, it fetches all users who are not in that group.
    If the 'Supervisor' group doesn't exist, it fetches all users.

    The response is a JSON object where the keys are user IDs and the values are the usernames.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        JsonResponse: A JSON response containing a dictionary of user IDs and usernames.
    """
    try:
        supervisor_group = Group.objects.get(name='Supervisor')
        users = User.objects.exclude(groups=supervisor_group).values('id', 'username')
    except Group.DoesNotExist:
        users = User.objects.all().values('id', 'username')

    users_dict: Dict[int, str] = {user['id']: user['username'] for user in users}

    return JsonResponse(users_dict)


class AgentView(APIView):
    """
    Handles POST requests to trigger the agent logic.

    This view calls the `call_agent` function when a POST request is made. It expects
    a valid request body that the agent function can process.

    Methods:
        post: Calls the agent function with the request and returns an empty JSON response.
    """
    
    def post(self, request) -> JsonResponse:
        """
        Handle POST requests to trigger the agent function.

        Args:
            request (HttpRequest): The incoming POST request, containing the data for the agent.

        Returns:
            JsonResponse: A JSON response indicating that the request was processed successfully.
        """
        call_agent(request)
        return JsonResponse({})
