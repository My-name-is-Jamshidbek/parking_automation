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
    status = models.BooleanField(default=False)  # New status field with default set to False

    def __str__(self):
        return self.place_name


# New Customer model
class Customer(models.Model):
    fullname = models.CharField(max_length=255, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, editable=False)
    seat = models.ForeignKey('Seat', on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=255)
    arrival_time = models.DateTimeField(default=timezone.now)
    leave_time = models.DateTimeField(null=True, blank=True, default=timezone.now() + datetime.timedelta(hours=2))
    stay_time = models.DurationField(null=True, blank=True, editable=False)
    hourly_price = models.ForeignKey('Price', on_delete=models.SET_NULL, null=True)
    total_price = models.BigIntegerField(default=0, editable=False)
    carname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.fullname or f"Customer {self.id}"

    def customer_is_gone(self):
        """ Update leave time and calculate the total price when a customer leaves """
        self.leave_time = timezone.now()
        if self.arrival_time and self.leave_time:
            self.stay_time = self.leave_time - self.arrival_time
            self.total_price = (self.stay_time.total_seconds() / 3600) * self.hourly_price.price
        self.save()
        return self.total_price, self.stay_time.total_seconds(), self.vehicle_number
