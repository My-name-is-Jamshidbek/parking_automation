# urls.py
from django.urls import path
from .views import home_view
from .price_views import PriceListView, PriceCreateView, PriceUpdateView, PriceDeleteView
from .seats_views import SeatListView, SeatCreateView, SeatDeleteView, SeatUpdateView

urlpatterns = [
    path('prices/', PriceListView.as_view(), name='price-list'),
    path('prices/add/', PriceCreateView.as_view(), name='price-add'),
    path('prices/<int:pk>/update/', PriceUpdateView.as_view(), name='price-update'),
    path('prices/<int:pk>/delete/', PriceDeleteView.as_view(), name='price-delete'),

    path('seats/', SeatListView.as_view(), name='seat-list'),
    path('seats/add/', SeatCreateView.as_view(), name='seat-add'),
    path('seats/<int:pk>/', SeatUpdateView.as_view(), name='seat-update'),
    path('seats/<int:pk>/delete/', SeatDeleteView.as_view(), name='seat-delete'),

    path('', home_view, name='home'),

]
