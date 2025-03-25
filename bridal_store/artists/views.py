from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from datetime import datetime, timedelta
from .models import Artist, Booking
from .forms import BookingForm

def artist_list(request):
    artists = Artist.objects.filter(available=True)
    return render(request, 'artists/artist_list.html', {'artists': artists})

def artist_detail(request, slug):
    artist = get_object_or_404(Artist, slug=slug, available=True)
    return render(request, 'artists/artist_detail.html', {'artist': artist})

@login_required
def booking_create(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id, available=True)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.artist = artist
            
            # Check for booking conflicts
            date = booking.date
            start_time = booking.time_start
            end_time = booking.time_end
            
            existing_bookings = Booking.objects.filter(
                artist=artist,
                date=date,
                status__in=['pending', 'confirmed']
            ).filter(
                Q(time_start__lt=end_time, time_end__gt=start_time)
            )
            
            if existing_bookings.exists():
                messages.error(request, "This time slot is already booked. Please choose another time.")
            else:
                booking.save()
                messages.success(request, f"Your booking with {artist.name} has been requested.")
                return redirect('accounts:profile')
    else:
        # Default to 1 hour appointment
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        form = BookingForm(initial={
            'date': tomorrow.date(),
            'time_start': '10:00',
            'time_end': '11:00',
        })
    
    return render(request, 'artists/booking_form.html', {
        'form': form,
        'artist': artist
    })

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'artists/booking_list.html', {'bookings': bookings})

@login_required
def booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if booking.status in ['pending', 'confirmed']:
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Your booking has been cancelled.")
    else:
        messages.error(request, "This booking cannot be cancelled.")
    
    return redirect('artists:booking_list')