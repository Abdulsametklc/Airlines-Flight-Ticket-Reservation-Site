from django.contrib import admin
from .models import Flight, Customer, FlightsBackup, CustomerSeats

@admin.register(Flight)
# Flight modelini admin paneline kaydeden sınıf
class FlightAdmin(admin.ModelAdmin):
    list_display = ('departure_city', 'arrival_city', 'departure_date', 'departure_time', 'arrival_time', 'price')
    list_filter = ('departure_city', 'arrival_city', 'departure_date')
    search_fields = ('departure_city', 'arrival_city')

@admin.register(Customer)
class CutsomerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone_number', 'selected_seat', 'flight')
    # Arama yapılabilecek alanlar
    search_fields = ('first_name', 'last_name', 'email', 'tc_number')
    # Filtreleme alanları
    list_filter = ('flight', 'selected_seat')

admin.site.register(FlightsBackup)
class FlightsBackupAdmin(admin.ModelAdmin):
    list_display = ('flight_id', 'departure_city', 'arrival_city', 'departure_date', 'backup_time')
    
admin.site.register(CustomerSeats)