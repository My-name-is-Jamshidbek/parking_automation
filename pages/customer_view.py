from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import make_naive
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from .models import Customer, Seat
from .requireds import staff_member_required_or_404


@method_decorator(staff_member_required_or_404, name='dispatch')
class CustomerCreateView(CreateView):
    model = Customer
    fields = ['fullname', 'seat', 'vehicle_number', 'arrival_time', 'leave_time', 'hourly_price', 'carname']
    template_name = 'customers/customer_form.html'

    def get_queryset(self):
        # Return only the seats where status is False
        return Seat.objects.filter(status=False)

    def form_valid(self, form):
        form.instance.user = self.request.user

        # Save the form to get the customer instance
        response = super().form_valid(form)

        # Set the seat's status to True after the customer is successfully created
        seat = form.instance.seat
        if seat:  # Ensure the seat exists
            seat.status = True
            seat.save()

        return response

    def get_success_url(self):
        return reverse_lazy('customer-list')


class CustomerUpdateView(UpdateView):
    model = Customer
    fields = ['fullname', 'seat', 'vehicle_number', 'arrival_time', 'leave_time', 'hourly_price', 'carname']
    template_name = 'customers/customer_form.html'

    def form_valid(self, form):
        # Check if the seat has changed
        if 'seat' in form.changed_data:
            old_seat = get_object_or_404(Seat, id=self.object.seat.id)
            new_seat = form.cleaned_data['seat']

            # Update old seat status if it's different from the new seat
            if old_seat != new_seat:
                old_seat.status = False
                old_seat.save()

                # Update new seat status
                new_seat.status = True
                new_seat.save()

        return super().form_valid(form)


    def get_success_url(self):
        return reverse_lazy('customer-list')


from django.views.generic import ListView
from django.http import HttpResponse
from .models import Customer
import pandas as pd
from django.utils.timezone import make_aware
from datetime import datetime

class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'

    def get_queryset(self, year=None, month=None):
        """ Modify queryset to filter by year and month of arrival_time if specified. """
        queryset = Customer.objects.filter()
        if year and month:
            start_date = make_aware(datetime(year, month, 1))
            if month == 12:
                end_date = make_aware(datetime(year + 1, 1, 1))
            else:
                end_date = make_aware(datetime(year, month + 1, 1))
            queryset = queryset.filter(arrival_time__range=(start_date, end_date))
        return queryset

    def post(self, request, *args, **kwargs):
        month_year = request.POST.get('monthYear', '')  # Assuming input is in 'MM-YYYY' format
        if month_year:
            try:
                month, year = int(month_year.split("-")[0]), int(month_year.split("-")[1])
                self.object_list = self.get_queryset(year=year, month=month)  # Set the object_list
                df = pd.DataFrame(list(self.object_list.values()))

                # Convert timezone-aware datetime fields to timezone-naive before exporting to Excel
                df['arrival_time'] = df['arrival_time'].apply(lambda x: make_naive(x, timezone.get_current_timezone()))
                if 'leave_time' in df.columns:
                    df['leave_time'] = df['leave_time'].apply(
                        lambda x: make_naive(x, timezone.get_current_timezone()) if pd.notnull(x) else x)

                # Export to Excel logic here
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )
                response['Content-Disposition'] = f'attachment; filename="customer_data_{year}_{month}.xlsx"'

                with pd.ExcelWriter(response, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Filtered Customers')

                return response
            except ValueError:
                # Handle invalid input format
                return self.render_to_response(
                    self.get_context_data(error="Invalid date format. Please use MM-YYYY format."))

        # Handle case where monthYear is not provided or invalid
        self.object_list = self.get_queryset()  # Ensure this is set even if no POST data or invalid
        return self.render_to_response(self.get_context_data())
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error'] = kwargs.get('error', '')  # Pass error messages if any
        return context


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        # Retrieve the object to get access to the related seat
        self.object = self.get_object()
        seat = self.object.seat  # Assuming there's a foreign key from Customer to Seat

        # Proceed with the standard delete operation
        response = super().delete(request, *args, **kwargs)

        # After successfully deleting the customer, update the seat status
        if seat:  # Check if the seat exists
            seat.status = False
            seat.save()

        return response

    def get_success_url(self):
        return reverse_lazy('customer-list')


def customer_gone_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    tp, ts, vn = customer.customer_is_gone()

    if customer.seat:  # Check if the customer has an associated seat
        customer.seat.status = False  # Set the seat status to False
        customer.seat.save()  # Save the seat

    # Formatting the stay time from duration to readable format
    stay_seconds = ts
    hours, remainder = divmod(stay_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    stay_formatted = f"{int(hours)}h {int(minutes)}min"

    # Formatting the total price to two decimal places
    formatted_price = f"{tp:.2f}"

    # Prepare message
    messages.success(request, f'Customer has gone. Total price: ${formatted_price}, Stay time: {stay_formatted}, Vehicle number: {vn}')

    return redirect('customer-list')


class CustomerHistoryView(ListView):
    model = Customer
    template_name = 'customers/customer_history.html'
    context_object_name = 'customers'  # This is the name to use in the template to loop over the customers
    def get_queryset(self):
        # Filter customers who have both stay_time and total_price defined (non-null and non-zero)
        return Customer.objects.exclude(stay_time__isnull=True).exclude(total_price=0)