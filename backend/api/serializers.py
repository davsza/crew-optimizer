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
        """
        Meta class for UserSerializer.

        This inner class defines the configuration for the serializer, specifying 
        the model to be serialized and the fields to include in the serialized output.

        Attributes:
            model (Model): The Django model that this serializer is associated with. 
                            In this case, it is the `User` model.
            fields (list): A list of field names that should be included in the serialized data. 
                           Here, the fields are 'id', 'username', and 'password'.
            extra_kwargs (dict): A dictionary of extra keyword arguments to customize 
                                  field-level behaviors. In this case, the password field is 
                                  marked as write-only, meaning it will not be included in 
                                  serialized output but can be set during user creation.
        """
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

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
        day_off_call_in_days (str): A string representing the day off call-in days for the roster.
        vacation (str): A string representing the vacation days for the roster.
        sickness (str): A string representing the sickness days for the roster.
        published (bool): A flag indicating whether the roster is published.
        reserve_call_in (bool): A flag indicating if a call-in is needed for reserve days.
        day_off_call_in (bool): A flag indicating if a call-in is needed for day off days.
        owner (User): The user who owns the roster, read-only.
    """

    class Meta:
        """
        Meta class for RosterSerializer.

        This inner class defines the configuration for the serializer, including the model 
        to be serialized, the fields that should be included in the serialized output, 
        and additional customization of field behaviors.

        Attributes:
            model (Model): The Django model that this serializer is associated with. 
                            In this case, it is the `Roster` model.
            fields (list): A list of field names that should be included in the serialized data. 
                           It includes various roster-related fields such as `week_number`, 
                           `schedule`, `work_days`, etc.
            extra_kwargs (dict): A dictionary of extra keyword arguments to customize 
                                  field-level behaviors. Here, the `owner` field is marked 
                                  as read-only, meaning it cannot be modified during 
                                  serialization but can be included in the output.
        """
        model = Roster
        fields = [
            "id", "week_number", "year", "application", "schedule", "work_days", 
            "off_days", "reserve_days", "reserve_call_in_days", "day_off_call_in_days", "vacation", 
            "sickness", "published", "reserve_call_in", "day_off_call_in", "owner"
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
        """
        Meta class for MessageSerializer.

        This inner class configures the serializer for the `Message` model. It defines which fields 
        are serialized, and provides additional customizations such as marking fields as read-only.

        Attributes:
            model (Model): The Django model that this serializer is associated with. 
                            In this case, it is the `Message` model.
            fields (list): A list of field names to include in the serialized data. 
                           It includes fields such as `id`, `text`, `date`, `sent_by_user`,
                           and `owner`.
            extra_kwargs (dict): A dictionary of extra keyword arguments to customize 
                                  the behavior of specific fields. The `owner` field is marked 
                                  as read-only, meaning it will be included in the serialized output 
                                  but cannot be modified when creating or updating a `Message`.
        """
        model = Message
        fields = ["id", "text", "date", "sent_by_user", "owner"]
        extra_kwargs = {"owner": {"read_only": True}}
