from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import generics
from rest_framework.views import APIView
from .serializers import UserSerializer, ShiftSerializer, MessageSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Shift, Message
from django.http import JsonResponse
from .agent import call_agent


class ShiftGivenWeekQuery(generics.ListAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        week = self.kwargs.get('week')
        return Shift.objects.filter(owner=user, week=week)


class ShiftGivenWeekQueryAdmin(generics.ListAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        week = self.kwargs.get('week')
        supervisor_group = Group.objects.get(name='Supervisor')
        return Shift.objects.filter(week=week).exclude(owner__groups=supervisor_group)


class ShiftLastWeeksQuery(generics.ListAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        week = self.kwargs.get('week')
        return Shift.objects.filter(owner=user, week__lte=week)


class MessageListCreate(generics.ListCreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Message.objects.filter(owner=user).order_by('-id')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ShiftListCreate(generics.ListCreateAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Shift.objects.filter(owner=user)


class ShiftDelete(generics.DestroyAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Shift.objects.filter(owner=user)


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
        return JsonResponse({"a": "b"})
