from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.timezone import make_naive
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, redirect
from .models import Customer, Seat
from .requireds import staff_member_required_or_404
from openpyxl.styles import Alignment, Font
from django.views.generic import ListView
from django.http import HttpResponse
from .models import Customer
import pandas as pd
from django.utils.timezone import make_aware
from datetime import datetime


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


class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'
    context_object_name = 'customers'

    def get_queryset(self):
        """ Default queryset for GET request. """
        return Customer.objects.all()

    def filter_queryset_by_date(self, year, month):
        """ Filter the queryset based on year and month. """
        start_date = make_aware(datetime(year, month, 1))
        end_date = make_aware(datetime(year, month + 1, 1)) if month < 12 else make_aware(datetime(year + 1, 1, 1))
        return Customer.objects.filter(arrival_time__range=(start_date, end_date))

    def post(self, request, *args, **kwargs):
        month_year = request.POST.get('monthYear', '')
        if month_year:
            try:
                month, year = int(month_year.split("-")[0]), int(month_year.split("-")[1])
                filtered_customers = self.filter_queryset_by_date(year, month)

                df = pd.DataFrame(list(filtered_customers.values(
                    'fullname', 'carname', 'arrival_time', 'leave_time', 'hourly_price', 'seat'  # Specify other fields as required
                )))

                # Convert timezone-aware datetime fields to timezone-naive before exporting to Excel
                if 'arrival_time' in df:
                    df['arrival_time'] = df['arrival_time'].apply(lambda x: make_naive(x, timezone.get_current_timezone()))
                if 'leave_time' in df:
                    df['leave_time'] = df['leave_time'].apply(
                        lambda x: make_naive(x, timezone.get_current_timezone()) if pd.notnull(x) else x)

                # Set up the HTTP response as an Excel file
                response = HttpResponse(
                    content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )
                response['Content-Disposition'] = f'attachment; filename="customer_data_{year}_{month}.xlsx"'

                # Save DataFrame to Excel
                # Export to Excel and set column widths
                with pd.ExcelWriter(response, engine='openpyxl') as writer:
                    df.to_excel(writer, index=False, sheet_name='Filtered Customers')
                    workbook = writer.book
                    worksheet = writer.sheets['Filtered Customers']

                    # Adjust column widths based on the longest entry in each column
                    for column_cells in worksheet.columns:
                        length = max(len(str(cell.value)) for cell in column_cells)
                        worksheet.column_dimensions[column_cells[0].column_letter].width = length+5

                    # Set a default font and alignment for all cells
                    for row in worksheet.iter_rows():
                        for cell in row:
                            cell.alignment = Alignment(horizontal='center', vertical='center')
                            cell.font = Font(name='Calibri', size=12)
                    names = ['Полное имя', 'Название автомобиля', 'Время прибытия', 'Оставьте время', 'Почасовая цена',
                             'Место']
                    for index, name in enumerate(names, start=1):
                        cell_reference = worksheet.cell(row=1,
                                                        column=index)  # This targets cells A1, B1, C1, etc., dynamically
                        cell_reference.value = name
                        cell_reference.font = Font(bold=True)  # Optional: Make header bold

                return response
            except ValueError:
                context = self.get_context_data(error="Invalid date format. Please use MM-YYYY format.")
                return self.render_to_response(context)

        # If POST data is incorrect or missing, simply render the list
        return self.render_to_response(self.get_context_data())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['error'] = kwargs.get('error', '')
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