from django.db import models
from django.contrib.auth.models import User
from .utils.constants import NUMBER_OF_DAYS, NUMBER_OF_SHIFTS, MESSAGE_MAX_LENGTH


class Roster(models.Model):
    week_number = models.IntegerField()
    year = models.IntegerField()
    application = models.CharField(max_length=NUMBER_OF_SHIFTS)
    schedule = models.CharField(max_length=NUMBER_OF_SHIFTS)
    modification = models.CharField(max_length=NUMBER_OF_SHIFTS)
    work_days = models.CharField(max_length=NUMBER_OF_DAYS)
    off_days = models.CharField(max_length=NUMBER_OF_DAYS)
    reserve_days = models.CharField(max_length=NUMBER_OF_DAYS)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shifts")


class Message(models.Model):
    text = models.CharField(max_length=MESSAGE_MAX_LENGTH)
    date = models.DateTimeField(auto_now_add=True)
    sent_by_user = models.BooleanField()
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="messages")
