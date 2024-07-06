from django.db import models
from django.contrib.auth.models import User
from constants import NUMBER_OF_SHIFTS, NUMBER_OF_DAYS

# Create your models here.


class Shift(models.Model):
    week = models.IntegerField()
    year = models.IntegerField()
    applied_shift = models.CharField(max_length=NUMBER_OF_SHIFTS)
    actual_shift = models.CharField(max_length=NUMBER_OF_SHIFTS)
    work_days = models.CharField(max_length=NUMBER_OF_DAYS)
    off_days = models.CharField(max_length=NUMBER_OF_DAYS)
    reserve_days = models.CharField(max_length=NUMBER_OF_DAYS)
    application_last_modified = models.DateTimeField(auto_now_add=True)
    actual_last_modified = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shifts")
