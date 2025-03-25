from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from .models import Category, Product, Order, OrderItem
from accounts.models import Profile
from .forms import OrderCreateForm
from decimal import Decimal
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import razorpay



razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


    
def landing(request):
    return render(request, 'shop/landing.html')

def home(request):
    return render(request, 'shop/landing.html', {
    })
    
def aboutus(request):
    return render(request, 'shop/aboutus.html')
    
def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    return render(request, 'shop/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'shop/product_detail.html', {'product': product})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    
    if product_id in cart:
        cart[product_id] += 1
    else:
        cart[product_id] = 1
    
    request.session['cart'] = cart
    messages.success(request, f'Added {product.name} to your cart.')
    return redirect('shop:product_list')

@login_required
def cart_detail(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total += subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal
        })
    
    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})    
    product_id = str(product_id)
    
    if product_id in cart:
        del cart[product_id]
        request.session['cart'] = cart
        messages.success(request, "Item removed from your cart.")
    
    return redirect('shop:cart_detail')

@login_required
def order_created(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_created.html', {'order': order})

@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('shop:product_list')

    cart_items = []
    subtotal = Decimal('0.00')

    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_subtotal = product.price * quantity
        subtotal += item_subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': item_subtotal
        })

    shipping_cost = Decimal('50.00')
    total_with_shipping = subtotal + shipping_cost

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)

        if form.is_valid():
            # Create the order in database before payment
            order = form.save(commit=False)
            order.user = request.user
            order.status = 'pending'  # Initial status is pending
            order.paid = False
            order.subtotal = subtotal
            order.shipping_cost = shipping_cost
            order.total = total_with_shipping
            order.save()
            
            # Create order items
            for product_id, quantity in cart.items():
                product = get_object_or_404(Product, id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    price=product.price,
                    quantity=quantity
                )
            
            # Store order ID in session
            request.session['order_id'] = order.id
            
            # Redirect to payment page with the order ID
            return redirect('shop:payment_page')
        else:
            messages.error(request, "Please fill in all required fields.")
    else:
        form = OrderCreateForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': getattr(request.user.profile, 'phone', ''),
            'address': getattr(request.user.profile, 'address', '')
        })

    return render(request, 'shop/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total_with_shipping
    })
    

@login_required
def payment(request):
    # Get order_id from session
    order_id = request.session.get('order_id')
    
    if not order_id:
        messages.error(request, "Order information not found. Please try again.")
        return redirect('shop:checkout')
    
    # Get the order from database
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Calculate the total using the method in your Order model
    total_price = order.get_total_cost()
    
    # Calculate amount in paise
    order_amount = max(int(total_price * 100), 100)  # Minimum ₹1.00
    
    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        order_currency = "INR"
        order_receipt = f"order_rcptid_{order.id}"
        
        razorpay_order = client.order.create({
            "amount": order_amount,
            "currency": order_currency,
            "receipt": order_receipt,
            "payment_capture": "1"
        })
        
        # Store Razorpay order ID in the order
        order.razorpay_order_id = razorpay_order.get("id")
        order.save()
        
        return render(request, 'shop/payment.html', {
            'order': order,
            'total': total_price,
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'razorpay_order_id': razorpay_order.get("id"),
            'amount_in_paise': order_amount,
            'callback_url': request.build_absolute_uri(reverse("shop:payment_callback")),
        })
    
    except Exception as e:
        messages.error(request, f"Payment gateway error: {str(e)}")
        return redirect('shop:checkout')
    
@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        signature = request.POST.get('razorpay_signature', '')
        
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        try:
            params_dict = {
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': razorpay_order_id,
                'razorpay_signature': signature
            }
            
            # Verify signature
            client.utility.verify_payment_signature(params_dict)
            
            # Find the order by Razorpay order ID
            order = get_object_or_404(Order, razorpay_order_id=razorpay_order_id)
            
            # Update order status
            order.paid = True
            order.status = 'confirmed'  # Change status to confirmed/paid
            order.payment_id = payment_id
            order.save()
            
            # Clear cart from session
            if 'cart' in request.session:
                del request.session['cart']
            
            # Clear order ID from session
            if 'order_id' in request.session:
                del request.session['order_id']
            
            messages.success(request, "Payment successful! Your order has been confirmed.")
            return redirect('shop:order_created', order_id=order.id)
            
        except Exception as e:
            messages.error(request, f"Payment verification failed: {str(e)}")
            return render(request, 'shop/payment_failed.html', {'error': str(e)})
    
    return redirect('shop:checkout')
@login_required
def prepare_order(request):
    cart = request.session.get('cart', {})
    
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('shop:product_list')
    
    # Calculate totals
    cart_items = []
    subtotal = Decimal('0.00')
    
    for product_id, quantity in cart.items():
        product = get_object_or_404(Product, id=product_id)
        item_subtotal = product.price * quantity
        subtotal += item_subtotal
        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': item_subtotal
        })
    
    shipping_cost = Decimal('50.00')
    total_with_shipping = subtotal + shipping_cost
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            # Store order info in session instead of creating the order
            order_data = {
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': form.cleaned_data['email'],
                'address': form.cleaned_data['address'],
                'phone': form.cleaned_data['phone'],
                'cart': cart,
                'subtotal': str(subtotal),
                'shipping_cost': str(shipping_cost),
                'total': str(total_with_shipping)
            }
            
            request.session['pending_order'] = order_data
            
            # Create Razorpay order
            amount_in_paise = int(total_with_shipping * 100)
            
            razorpay_order = razorpay_client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'payment_capture': '1'  # Auto-capture
            })
            
            request.session['razorpay_order_id'] = razorpay_order['id']
            
            return redirect('shop:payment_page')
    else:
        form = OrderCreateForm(initial={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': getattr(request.user.profile, 'phone', ''),
            'address': getattr(request.user.profile, 'address', '')
        })
    
    return render(request, 'shop/checkout.html', {
        'form': form,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total_with_shipping
    })
    
# Fix for payment_page view
@login_required
def payment_page(request):
    order_id = request.session.get('order_id')
    if not order_id:
        messages.error(request, "Order information not found. Please try again.")
        return redirect("shop:checkout")
    
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Create Razorpay order
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    
    try:
        amount_in_paise = int(order.total * 100)
        order_currency = "INR"
        order_receipt = f"order_rcptid_{order.id}"
        
        razorpay_order = client.order.create({
            "amount": amount_in_paise,
            "currency": order_currency,
            "receipt": order_receipt,
            "payment_capture": "1"
        })
        
        # Store Razorpay order ID in the Order model
        order.razorpay_order_id = razorpay_order.get("id")
        order.save()
        
    except Exception as e:
        messages.error(request, f"Payment gateway error: {str(e)}")
        return redirect("shop:checkout")
    
    context = {
        "order": order,
        "total": order.total,
        "amount_in_paise": amount_in_paise,
        "razorpay_key_id": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": razorpay_order.get("id"),
        "callback_url": request.build_absolute_uri(reverse("shop:payment_callback")),
        "merchant_name": "Truly Wed",
        "user": request.user,
        "csrf_token": get_token(request),
    }
    
    return render(request, "shop/payment.html", context)
@login_required
def razorpay_payment(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    total = sum(item.price * item.quantity for item in order.orderitem_set.all())

    # Razorpay Integration (Modify as needed)
    razorpay_order = {
        "amount": int(total * 100),  
        "currency": "INR",
        "receipt": f"order_{order.id}",
    }

    return render(request, 'shop/razorpay_payment.html', {
        'order': order,
        'total': total,
        'razorpay_order': razorpay_order
    })
    
from django.middleware.csrf import get_token

def payment_view(request):
    order_amount = 405100  # Amount in paise (Rs 4051.00)
    order_currency = "INR"
    
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
    payment_order = client.order.create({
        "amount": order_amount,
        "currency": order_currency,
        "payment_capture": 1  # Auto capture
    })

    context = {
        "razorpay_key_id": settings.RAZORPAY_KEY_ID, 
        "razorpay_order_id": payment_order["id"],
        "amount_in_paise": order_amount,
        "merchant_name": "Your Store Name",
        "callback_url": reverse("payment_callback"),
        "csrf_token": get_token(request)  # Ensure CSRF token is included
    }