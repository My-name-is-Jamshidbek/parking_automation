# urls.py
from django.urls import path
from .views import home_view
from .price_views import PriceListView, PriceCreateView, PriceUpdateView, PriceDeleteView
from .seats_views import SeatListView, SeatCreateView, SeatDeleteView, SeatUpdateView, AvailableSeatsView
from .customer_view import (CustomerListView, CustomerCreateView, CustomerUpdateView, CustomerDeleteView,
                            CustomerHistoryView, customer_gone_view)

urlpatterns = [
    path('prices/', PriceListView.as_view(), name='price-list'),
    path('prices/add/', PriceCreateView.as_view(), name='price-add'),
    path('prices/<int:pk>/update/', PriceUpdateView.as_view(), name='price-update'),
    path('prices/<int:pk>/delete/', PriceDeleteView.as_view(), name='price-delete'),

    path('seats/', SeatListView.as_view(), name='seat-list'),
    path('seats/add/', SeatCreateView.as_view(), name='seat-add'),
    path('seats/<int:pk>/', SeatUpdateView.as_view(), name='seat-update'),
    path('seats/<int:pk>/delete/', SeatDeleteView.as_view(), name='seat-delete'),
    path('available-seats/', AvailableSeatsView.as_view(), name='available-seats'),

    path('customers/', CustomerListView.as_view(), name='customer-list'),
    path('customers/add/', CustomerCreateView.as_view(), name='customer-add'),
    path('customers/<int:pk>/', CustomerUpdateView.as_view(), name='customer-update'),
    path('customers/<int:pk>/delete/', CustomerDeleteView.as_view(), name='customer-delete'),
    path('customers/<int:pk>/gone/', customer_gone_view, name='customer-gone'),
    path('customer-history/', CustomerHistoryView.as_view(), name='customer-history'),

    path('', home_view, name='home'),

]
