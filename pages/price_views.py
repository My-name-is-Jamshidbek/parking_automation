# views.py
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from .requireds import staff_member_required_or_404
from .models import Price


@method_decorator(staff_member_required_or_404, name='dispatch')
class PriceListView(ListView):
    model = Price
    context_object_name = 'prices'
    template_name = 'prices/price_list.html'


@method_decorator(staff_member_required_or_404, name='dispatch')
class PriceCreateView(CreateView):
    model = Price
    fields = ['price', 'description']
    template_name = 'prices/price_form.html'
    success_url = reverse_lazy('price-list')


@method_decorator(staff_member_required_or_404, name='dispatch')
class PriceUpdateView(UpdateView):
    model = Price
    fields = ['price', 'description']
    context_object_name = 'price'
    template_name = 'prices/price_form.html'
    success_url = reverse_lazy('price-list')


@method_decorator(staff_member_required_or_404, name='dispatch')
class PriceDeleteView(DeleteView):
    model = Price
    context_object_name = 'price'
    template_name = 'prices/price_confirm_delete.html'
    success_url = reverse_lazy('price-list')
