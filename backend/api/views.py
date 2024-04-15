from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework import generics
from .serializers import UserSerializer, ShiftSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Shift


class ShiftListCreate(generics.ListCreateAPIView):
    serializer_class = ShiftSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Shift.objects.filter(owner=user)

    def perform_create(self, serializer):
        existing_shift = Shift.objects.filter(owner=self.request.user).first()
        if existing_shift:
            print("Shift already exists")
            serializer.update(existing_shift, serializer.validated_data)
        else:
            print("Creating new shift")
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
