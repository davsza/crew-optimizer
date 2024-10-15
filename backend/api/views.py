from django.contrib.auth.models import Group, User
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from .agent import call_agent
from .models import Message, Roster
from .serializers import MessageSerializer, RosterSerializer, UserSerializer


class RosterGivenWeekQuery(generics.ListAPIView):
    serializer_class = RosterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        week_number = self.kwargs.get('week_number')
        return Roster.objects.filter(owner=user, week_number=week_number)


class RosterGivenWeekQueryAdmin(generics.ListAPIView):
    serializer_class = RosterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        week_number = self.kwargs.get('week_number')
        supervisor_group = Group.objects.get(name='Supervisor')
        return Roster.objects.filter(week_number=week_number).exclude(owner__groups=supervisor_group)


class RosterLastWeeksQuery(generics.ListAPIView):
    serializer_class = RosterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        week_number = self.kwargs.get('week_number')
        return Roster.objects.filter(owner=user, week_number__lte=week_number)


class MessageListCreate(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(owner=user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class RosterListCreate(generics.ListCreateAPIView):
    serializer_class = RosterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Roster.objects.filter(owner=user)


class RosterDelete(generics.DestroyAPIView):
    serializer_class = RosterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Roster.objects.filter(owner=user)


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class UserDataView(APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            user_groups = user.groups.all()
            group_name = None
            if user_groups.exists():
                group = user_groups.first()
                group_name = group.name

            return JsonResponse({'username': user.username, 'group': group_name})
        else:
            return JsonResponse({'error': 'User is not authenticated'}, status=401)


def get_user_details(request):
    try:
        supervisor_group = Group.objects.get(name='Supervisor')
        users = User.objects.exclude(
            groups=supervisor_group).values('id', 'username')
    except Group.DoesNotExist:
        users = User.objects.all().values('id', 'username')

    user_dict = {user['id']: user['username'] for user in users}
    return JsonResponse(user_dict)


class AgentView(APIView):
    def post(self, request):
        call_agent(request)
        return JsonResponse({})
