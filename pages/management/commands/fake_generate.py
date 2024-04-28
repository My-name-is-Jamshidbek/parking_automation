from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import get_user_model
import datetime
from faker import Faker
from pages.models import Customer, Seat, Price  # Adjust to your app's model import path


class Command(BaseCommand):
    help = 'Generates fake data for the models'

    def handle(self, *args, **options):
        fake = Faker()

        # Generating fake data for Price
        prices = [
            Price(price=fake.random_number(digits=6), description=fake.text(max_nb_chars=200))
            for _ in range(10)
        ]

        # Generating fake data for Seat
        seats = [
            Seat(place_name=fake.street_name(), explanation=fake.text(max_nb_chars=200), status=fake.boolean())
            for _ in range(100)
        ]

        with transaction.atomic():
            Price.objects.bulk_create(prices)
            Seat.objects.bulk_create(seats)

        seats = list(Seat.objects.all())
        prices = list(Price.objects.all())

        # Generating fake data for Customer
        User = get_user_model()
        users = list(User.objects.all())  # Assuming users are already created
        if not users:
            self.stdout.write(self.style.ERROR('No users found. Please create some users first.'))
            return

        customers = [
            Customer(
                fullname=fake.name(),
                user=fake.random.choice(users),
                seat=fake.random.choice(seats),
                vehicle_number=fake.license_plate(),
                arrival_time=timezone.now() - datetime.timedelta(hours=fake.random_int(min=1, max=24)),
                leave_time=timezone.now(),
                hourly_price=fake.random.choice(prices),
                total_price=fake.random_number(digits=5),
                carname=fake.company()
            )
            for _ in range(1000)
        ]

        with transaction.atomic():
            Customer.objects.bulk_create(customers)

        self.stdout.write(self.style.SUCCESS('Successfully generated fake data.'))

