from django.urls import path
from . import views

app_name = 'artists'

urlpatterns = [
    path('', views.artist_list, name='artist_list'),
    path('<slug:slug>/', views.artist_detail, name='artist_detail'),
    path('booking/<int:artist_id>/', views.booking_create, name='booking_create'),
    path('bookings/', views.booking_list, name='booking_list'),
    path('booking/cancel/<int:booking_id>/', views.booking_cancel, name='booking_cancel'),
]