from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Shift, Message


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_knwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ["id", "week", "year", "applied_shift", "actual_shift", "work_days", "off_days", "reserve_days",
                  "owner"]
        extra_kwargs = {"owner": {"read_only": True}}


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ["id", "text", "date", "sent_by_user", "owner"]
        extra_kwargs = {"owner": {"read_only": True}}
