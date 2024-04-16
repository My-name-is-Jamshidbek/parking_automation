from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db import models
from django.conf import settings  # If you're using the default auth user model
from django.utils import timezone
import datetime

# Existing Price model
class Price(models.Model):
    price = models.BigIntegerField()
    description = models.TextField()  # Assuming this is a text description; change the field type if it's not text

    def __str__(self):
        return self.description  # I've corrected this to return a string representation of description


# Existing Seat model
class Seat(models.Model):
    place_name = models.CharField(max_length=255)  # The max_length should be defined based on your varchar requirements
    explanation = models.TextField(null=True, blank=True)  # The question mark indicates that this field can be null

    def __str__(self):
        return self.place_name


# New Customer model
class Customer(models.Model):
    fullname = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    seat = models.ForeignKey('Seat', on_delete=models.CASCADE, default=Seat.objects.first().pk)
    vehicle_number = models.CharField(max_length=255)
    arrival_time = models.DateTimeField(default=timezone.now)
    leave_time = models.DateTimeField(null=True, blank=True, default=timezone.now() + datetime.timedelta(hours=2))
    stay_time = models.DurationField(null=True, blank=True, editable=False)
    hourly_price = models.ForeignKey('Price', on_delete=models.SET_NULL, null=True, default=Price.objects.first().pk)
    total_price = models.BigIntegerField(default=0, editable=False)
    carname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.fullname or f"Customer {self.id}"
