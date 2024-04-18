from django.shortcuts import render
from .models import Seat, Customer, Price


def home_view(request):
    seats = Seat.objects.all()[:10]  # Get all seats
    prices = Price.objects.all()[:10]
    customers = Customer.objects.all()[:10]

    return render(request, 'home.html', {'seats': seats, 'customers': customers, 'prices': prices})
