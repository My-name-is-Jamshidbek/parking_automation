from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from .models import Customer, Seat


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


class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'

    def get_queryset(self):
        # Filter customers where total_price is 0 and stay_time is None
        return Customer.objects.filter(total_price=0, stay_time__isnull=True)


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