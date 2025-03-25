from django.db import models
from django.urls import reverse
from django.conf import settings

class Artist(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    photo = models.ImageField(upload_to='artists/', blank=True)
    bio = models.TextField()
    specialization = models.CharField(max_length=200)
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('artists:artist_detail', args=[self.slug])

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='bookings', on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, related_name='bookings', on_delete=models.CASCADE)
    date = models.DateField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('date', 'time_start')
        
    def __str__(self):
        return f'Booking for {self.artist.name} on {self.date}'
    
    def get_duration(self):
        """Calculate duration in hours"""
        start_time = self.time_start.hour + self.time_start.minute/60
        end_time = self.time_end.hour + self.time_end.minute/60
        return end_time - start_time
    
from decimal import Decimal

def get_total_cost(self):
    return Decimal(self.get_duration()) * self.artist.price_per_hour

