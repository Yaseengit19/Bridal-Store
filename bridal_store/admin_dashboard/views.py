from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum
from django.contrib.auth.models import User
from shop.models import Product, Category, Order, OrderItem
from artists.models import Artist, Booking
from accounts.models import Profile
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, F

# Admin check decorator
def is_admin(user):
    return user.is_authenticated and user.is_staff

# Dashboard
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Count statistics
    total_products = Product.objects.count()
    total_artists = Artist.objects.count()
    total_users = User.objects.filter(is_staff=False).count()
    
    # Orders statistics
    total_orders = Order.objects.count()
    recent_orders = Order.objects.order_by('-created')[:5]
    today = timezone.now().date()
    orders_today = Order.objects.filter(created__date=today).count()

    # Booking statistics
    total_bookings = Booking.objects.count()
    recent_bookings = Booking.objects.order_by('-created')[:5]
    pending_bookings = Booking.objects.filter(status='pending').count()
    
    # User statistics
    new_users_week = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).count()
    
    return render(request, 'admin_dashboard/dashboard.html', {
        'total_products': total_products,
        'total_artists': total_artists,
        'total_users': total_users,
        'total_orders': total_orders,
        'recent_orders': recent_orders,
        'orders_today': orders_today,
        'total_bookings': total_bookings,
        'recent_bookings': recent_bookings,
        'pending_bookings': pending_bookings,
        'new_users_week': new_users_week,
    })

# Products
@user_passes_test(is_admin)
def product_list(request):
    products = Product.objects.all().order_by('-created')
    return render(request, 'admin_dashboard/product_list.html', {'products': products})

@user_passes_test(is_admin)
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'admin_dashboard/detail.html', {'product': product})

@user_passes_test(is_admin)
def product_create(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        # Process form data
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        stock = request.POST.get('stock')
        available = request.POST.get('available') == 'on'
        
        # Validation
        if not name or not slug or not category_id:
            messages.error(request, 'Please fill all required fields')
            return render(request, 'admin_dashboard/product_create.html', {
                'categories': categories
            })
        
        # Create product
        try:
            category = Category.objects.get(id=category_id)
            product = Product(
                name=name,
                slug=slug,
                category=category,
                description=description,
                price=price,
                stock=stock,
                available=available
            )
            
            # Handle image upload
            if 'image' in request.FILES:
                product.image = request.FILES['image']
                
            product.save()
            messages.success(request, f'Product "{name}" created successfully!')
            return redirect('admin_dashboard:product_list')
        except Exception as e:
            messages.error(request, f'Error creating product: {str(e)}')
            
    return render(request, 'admin_dashboard/product_create.html', {
        'categories': categories
    })

@user_passes_test(is_admin)
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    categories = Category.objects.all()
    
    if request.method == 'POST':
        # Process form data
        product.name = request.POST.get('name')
        product.slug = request.POST.get('slug')
        product.category_id = request.POST.get('category')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.available = request.POST.get('available') == 'on'
        
        # Handle image upload
        if 'image' in request.FILES:
            product.image = request.FILES['image']
            
        try:
            product.save()
            messages.success(request, f'Product "{product.name}" updated successfully!')
            return redirect('admin_dashboard:product_detail', product_id=product.id)
        except Exception as e:
            messages.error(request, f'Error updating product: {str(e)}')
    
    return render(request, 'admin_dashboard/edit_product.html', {
        'product': product,
        'categories': categories
    })

@user_passes_test(is_admin)
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_name = product.name
        try:
            product.delete()
            messages.success(request, f'Product "{product_name}" deleted successfully!')
            return redirect('admin_dashboard:product_list')
        except Exception as e:
            messages.error(request, f'Error deleting product: {str(e)}')
            return redirect('admin_dashboard:product_detail', product_id=product.id)
            
    return render(request, 'admin_dashboard/delete_product.html', {'product': product})

# Categories
@user_passes_test(is_admin)
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'admin_dashboard/list.html', {'categories': categories})

@user_passes_test(is_admin)
def category_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        
        if not name or not slug:
            messages.error(request, 'Please fill all required fields')
            return render(request, 'admin_dashboard/create.html')
            
        try:
            Category.objects.create(name=name, slug=slug)
            messages.success(request, f'Category "{name}" created successfully!')
            return redirect('admin_dashboard:category_list')
        except Exception as e:
            messages.error(request, f'Error creating category: {str(e)}')
            
    return render(request, 'admin_dashboard/create.html')

@user_passes_test(is_admin)
def category_edit(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.name = request.POST.get('name')
        category.slug = request.POST.get('slug')
        
        try:
            category.save()
            messages.success(request, f'Category "{category.name}" updated successfully!')
            return redirect('admin_dashboard:category_list')
        except Exception as e:
            messages.error(request, f'Error updating category: {str(e)}')
    
    return render(request, 'admin_dashboard/edit.html', {'category': category})

@user_passes_test(is_admin)
def category_delete(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category_name = category.name
        try:
            category.delete()
            messages.success(request, f'Category "{category_name}" deleted successfully!')
            return redirect('admin_dashboard:category_list')
        except Exception as e:
            messages.error(request, f'Error deleting category: {str(e)}')
            
    return render(request, 'admin_dashboard/delete.html', {'category': category})

# Orders
@user_passes_test(is_admin)
def order_list(request):
    orders = Order.objects.all().order_by('-created')
    return render(request, 'admin_dashboard/order_list.html', {'orders': orders})

@user_passes_test(is_admin)
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()
    return render(request, 'admin_dashboard/order_detail.html', {
        'order': order,
        'order_items': order_items
    })

@user_passes_test(is_admin)
def order_update_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f'Order #{order.id} status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status value')
            
    return redirect('admin_dashboard:order_detail', order_id=order.id)

# Artists
@user_passes_test(is_admin)
def artist_list(request):
    artists = Artist.objects.all()
    return render(request, 'admin_dashboard/artist_list.html', {'artists': artists})

@user_passes_test(is_admin)
def artist_detail(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    bookings = artist.bookings.all().order_by('-date')[:10]
    return render(request, 'admin_dashboard/artist_detail.html', {
        'artist': artist,
        'bookings': bookings
    })

@user_passes_test(is_admin)
def artist_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        slug = request.POST.get('slug')
        bio = request.POST.get('bio')
        specialization = request.POST.get('specialization')
        price_per_hour = request.POST.get('price_per_hour')
        available = request.POST.get('available') == 'on'
        
        if not name or not slug:
            messages.error(request, 'Please fill all required fields')
            return render(request, 'admin_dashboard/artist_create.html')
            
        try:
            artist = Artist(
                name=name,
                slug=slug,
                bio=bio,
                specialization=specialization,
                price_per_hour=price_per_hour,
                available=available
            )
            
            if 'photo' in request.FILES:
                artist.photo = request.FILES['photo']
                
            artist.save()
            messages.success(request, f'Artist "{name}" created successfully!')
            return redirect('admin_dashboard:artist_list')
        except Exception as e:
            messages.error(request, f'Error creating artist: {str(e)}')
            
    return render(request, 'admin_dashboard/artist_create.html')

@user_passes_test(is_admin)
def artist_edit(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    
    if request.method == 'POST':
        artist.name = request.POST.get('name')
        artist.slug = request.POST.get('slug')
        artist.bio = request.POST.get('bio')
        artist.specialization = request.POST.get('specialization')
        artist.price_per_hour = request.POST.get('price_per_hour')
        artist.available = request.POST.get('available') == 'on'
        
        if 'photo' in request.FILES:
            artist.photo = request.FILES['photo']
            
        try:
            artist.save()
            messages.success(request, f'Artist "{artist.name}" updated successfully!')
            return redirect('admin_dashboard:artist_detail', artist_id=artist.id)
        except Exception as e:
            messages.error(request, f'Error updating artist: {str(e)}')
    
    return render(request, 'admin_dashboard/artist_edit.html', {'artist': artist})

# Bookings
@user_passes_test(is_admin)
def booking_list(request):
    bookings = Booking.objects.all().order_by('-date')
    return render(request, 'admin_dashboard/booking_list.html', {'bookings': bookings})

@user_passes_test(is_admin)
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    return render(request, 'admin_dashboard/booking_detail.html', {'booking': booking})

@user_passes_test(is_admin)
def booking_update_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status and new_status in dict(Booking.STATUS_CHOICES):
            booking.status = new_status
            booking.save()
            messages.success(request, f'Booking #{booking.id} status updated to {new_status}')
        else:
            messages.error(request, 'Invalid status value')
            
    return redirect('admin_dashboard:booking_detail', booking_id=booking.id)

# Users
@user_passes_test(is_admin)
def user_list(request):
    users = User.objects.filter(is_staff=False).order_by('-date_joined')
    return render(request, 'admin_dashboard/user_list.html', {'users': users})
def create_user(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            messages.success(request, "User created successfully!")

    return redirect('user_list')

@user_passes_test(is_admin)
def user_detail(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.profile
    orders = user.order_set.all().order_by('-created')
    bookings = user.bookings.all().order_by('-date')
    
    return render(request, 'admin_dashboard/detail.html', {
        'user': user,
        'profile': profile,
        'orders': orders,
        'bookings': bookings
    })
    
@user_passes_test(is_admin)
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        user.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('admin_dashboard:user_list')

    messages.error(request, "Invalid request.")
    return redirect('admin_dashboard:user_list')