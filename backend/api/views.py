from django.shortcuts import render
from django.contrib.auth.models import User, Group
from rest_framework import generics
from rest_framework.views import APIView
from .serializers import UserSerializer, ShiftSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Shift
from django.http import JsonResponse
from .solver import solve


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


class ShiftListCreate(generics.ListCreateAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Shift.objects.filter(owner=user)

    def perform_create(self, serializer):
        week_number = serializer.validated_data.get('week')
        existing_shift = Shift.objects.filter(
            owner=self.request.user, week=week_number).first()
        if existing_shift:
            serializer.update(existing_shift, serializer.validated_data)
        else:
            serializer.save(owner=self.request.user)


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


def get_success_button(request):
    result = {"result": solve()}
    return JsonResponse(result)
