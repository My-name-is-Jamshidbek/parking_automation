from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, ListView, DeleteView
from .models import Customer


class CustomerCreateView(CreateView):
    model = Customer
    fields = ['fullname', 'seat', 'vehicle_number', 'arrival_time', 'leave_time', 'hourly_price', 'carname']
    template_name = 'customers/customer_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('customer-list')


class CustomerUpdateView(UpdateView):
    model = Customer
    fields = ['fullname', 'seat', 'vehicle_number', 'arrival_time', 'leave_time', 'hourly_price', 'carname']
    template_name = 'customers/customer_form.html'

    def get_success_url(self):
        return reverse_lazy('customer-list')


class CustomerListView(ListView):
    model = Customer
    template_name = 'customers/customer_list.html'


class CustomerDeleteView(DeleteView):
    model = Customer
    template_name = 'customers/customer_confirm_delete.html'

    def get_success_url(self):
        return reverse_lazy('customer-list')
