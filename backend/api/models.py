from django.db import models
from django.contrib.auth.models import User
from constants import NUMBER_OF_SHIFTS

# Create your models here.


class Shift(models.Model):
    week = models.CharField(max_length=3)
    year = models.IntegerField()
    applied_shift = models.CharField(max_length=NUMBER_OF_SHIFTS)
    actual_shift = models.CharField(max_length=NUMBER_OF_SHIFTS)
    application_last_modified = models.DateTimeField(auto_now_add=True)
    actual_last_modified = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shifts")
