from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Roster, Message


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the User model.

    This serializer is used to handle the creation and serialization of `User` objects,
    including handling the password securely. It ensures that the password is not exposed
    during serialization but can be set during user creation.

    Fields:
        id (int): The unique identifier of the user.
        username (str): The username of the user.
        password (str): The password for the user, write-only.
    """

    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}  # Corrected typo from extra_knwargs to extra_kwargs

    def create(self, validated_data: dict) -> User:
        """
        Create a new user with the provided validated data.

        Args:
            validated_data (dict): A dictionary containing the validated user data.

        Returns:
            User: The newly created user object.
        """
        # Use Django's create_user method to ensure the password is hashed properly
        user = User.objects.create_user(**validated_data)
        return user


class RosterSerializer(serializers.ModelSerializer):
    """
    Serializer for the Roster model.

    This serializer is used to convert the `Roster` model instances into JSON format
    and vice versa. It includes fields for various roster attributes, such as week number, 
    year, schedules, vacation, sickness, and more.

    Fields:
        id (int): The unique identifier of the roster.
        week_number (int): The week number for the roster.
        year (int): The year associated with the roster.
        application (str): The application data for the roster, typically a string representing
                           a sequence of applications.
        schedule (str): A string representing the worker's schedule for the week.
        work_days (str): A string representing the work days for the roster.
        off_days (str): A string representing the off days for the roster.
        reserve_days (str): A string representing the reserve days for the roster.
        reserve_call_in_days (str): A string representing the reserve call-in days for the roster.
        vacation (str): A string representing the vacation days for the roster.
        sickness (str): A string representing the sickness days for the roster.
        published (bool): A flag indicating whether the roster is published.
        reserve_call_in (bool): A flag indicating if a call-in is needed for reserve days.
        owner (User): The user who owns the roster, read-only.
    """

    class Meta:
        model = Roster
        fields = [
            "id", "week_number", "year", "application", "schedule", "work_days", 
            "off_days", "reserve_days", "reserve_call_in_days", "vacation", 
            "sickness", "published", "reserve_call_in", "owner"
        ]
        extra_kwargs = {"owner": {"read_only": True}}


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for the Message model.

    This serializer is used to convert the `Message` model instances into JSON format
    and vice versa. It includes fields for the message's ID, text, date, sender, and owner.
    
    Fields:
        id (int): The unique identifier of the message.
        text (str): The content of the message.
        date (datetime): The date when the message was created.
        sent_by_user (bool): Indicates whether the message was sent by a user.
        owner (User): The owner (user) associated with the message, read-only.
    """
    
    class Meta:
        model = Message
        fields = ["id", "text", "date", "sent_by_user", "owner"]
        extra_kwargs = {"owner": {"read_only": True}}
