from django.urls import path
from . import views
from .views import admin_dashboard
from django.contrib.auth import views as auth_views

app_name = 'admin_dashboard'

urlpatterns = [
    # Dashboard
    path('', admin_dashboard, name='admin_dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin_dashboard/order_list/', views.order_list, name='order_list'),
    path('admin_dashboard/orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('admin_dashboard/orders/<int:order_id>/update/', views.order_update_status, name='order_update_status'),


    
    # Products
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    
    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.order_update_status, name='order_update_status'),
    
    # Artists
    path('artists/', views.artist_list, name='artist_list'),
    path('artists/create/', views.artist_create, name='artist_create'),
    path('artists/<int:artist_id>/', views.artist_detail, name='artist_detail'),
    path('artists/<int:artist_id>/edit/', views.artist_edit, name='artist_edit'),
    
    # Bookings
    path('bookings/', views.booking_list, name='booking_list'),
    path('bookings/<int:booking_id>/', views.booking_detail, name='booking_detail'),
    path('bookings/<int:booking_id>/update-status/', views.booking_update_status, name='booking_update_status'),
    
    # Users
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.create_user, name='create_user'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),  # Add this line
]