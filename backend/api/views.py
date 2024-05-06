from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework.views import APIView
from .serializers import UserSerializer, ShiftSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Shift
from django.http import JsonResponse
import datetime
from django.db.models import Q


class ShiftListCreate(generics.ListCreateAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        current_date = datetime.datetime.now()
        current_week = current_date.isocalendar()[1]
        last_week = current_week - 1
        return Shift.objects.filter(owner=user).filter(Q(week="W"+str(current_week)) | Q(week="W"+str(last_week)))

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
