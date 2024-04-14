from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Shift


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
        fields = ["id", "week", "applied_shift", "actual_shift",
                  "application_last_modified", "actual_last_modified", "owner"]
        extra_kwargs = {"owner": {"read_only": True}}
