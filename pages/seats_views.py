from django.urls import reverse_lazy
from django.db.models import Count, Q
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from .models import Seat
from .requireds import staff_member_required_or_404

class SeatListView(ListView):
    model = Seat
    template_name = 'seats/seat_list.html'


@method_decorator(staff_member_required_or_404, name='dispatch')
class SeatCreateView(CreateView):
    model = Seat
    fields = ['place_name', 'explanation']
    template_name = 'seats/seat_form.html'
    success_url = reverse_lazy('seat-list')


@method_decorator(staff_member_required_or_404, name='dispatch')
class SeatUpdateView(UpdateView):
    model = Seat
    fields = ['place_name', 'explanation']
    template_name = 'seats/seat_form.html'
    success_url = reverse_lazy('seat-list')


@method_decorator(staff_member_required_or_404, name='dispatch')
class SeatDeleteView(DeleteView):
    model = Seat
    template_name = 'seats/seat_confirm_delete.html'
    success_url = reverse_lazy('seat-list')


class AvailableSeatsView(ListView):
    model = Seat
    template_name = 'seats/available_seats.html'
    context_object_name = 'seats'

    def get_queryset(self):
        return Seat.objects.filter(status=False)