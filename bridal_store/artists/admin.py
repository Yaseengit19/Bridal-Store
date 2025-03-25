from django.contrib import admin
from .models import Artist, Booking

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'specialization', 'price_per_hour', 'available']
    list_filter = ['available', 'specialization']
    list_editable = ['price_per_hour', 'available']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'bio', 'specialization']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['artist', 'user', 'date', 'time_start', 'time_end', 'status']
    list_filter = ['status', 'date', 'artist']
    search_fields = ['user__username', 'artist__name', 'notes']
    raw_id_fields = ['user', 'artist']
    date_hierarchy = 'date'
    