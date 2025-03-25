from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('aboutus/', views.aboutus, name='aboutus'),
    path('landing/', views.landing, name='landing'),
    path('products/', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('checkout/', views.checkout, name='checkout'),
    # path('order-created/<int:order_id>/', views.order_created, name='order_created'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('payment/', views.payment, name='payment_page'),  # ✅ Payment page before order creation
    path('payment/<int:order_id>/', views.razorpay_payment, name='razorpay_payment'),  # ✅ Razorpay after order is created
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('order/<int:order_id>/created/', views.order_created, name='order_created'),
    
]
