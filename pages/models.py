from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.db import models
from django.conf import settings  # If you're using the default auth user model


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
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=255)
    arrival_time = models.DateTimeField()
    leave_time = models.DateTimeField(null=True, blank=True)
    stay_time = models.DurationField(null=True, blank=True)
    hourly_price = models.BigIntegerField()  # Changed from ForeignKey to BigIntegerField
    total_price = models.BigIntegerField()
    carname = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return self.fullname or f"Customer {self.id}"


@receiver(pre_delete, sender=Price)
def update_hourly_price(sender, instance, **kwargs):
    customers = Customer.objects.filter(hourly_price=instance.price)
    for customer in customers:
        customer.hourly_price = instance.price  # Set to the price of the Price instance being deleted
        customer.save()
