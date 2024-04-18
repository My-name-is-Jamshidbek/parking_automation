from django.contrib import admin
from .models import Customer, Seat, Price  # Import your models here

# Simple registration
admin.site.register(Seat)
admin.site.register(Price)

# Customizing admin for the Customer model
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('fullname', 'seat', 'vehicle_number', 'arrival_time', 'leave_time', 'hourly_price', 'carname', 'user')  # Fields to display in the admin list view
    list_filter = ('seat', 'user')  # Fields to filter by in the admin list view
    search_fields = ('fullname', 'vehicle_number', 'carname')  # Fields to search in the admin list view

# Register Customer with the customized admin
admin.site.register(Customer, CustomerAdmin)
