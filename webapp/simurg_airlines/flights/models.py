from django.db import models

class Flight(models.Model):
    departure_city = models.CharField(max_length=50)
    arrival_city = models.CharField(max_length=50)
    departure_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    departure_time = models.TimeField(null = True, blank = True)
    arrival_time = models.TimeField(null = True, blank = True)
    def calculate_flight_duration(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT dbo.CalculateFlightDuration(%s)", [self.id])
            return cursor.fetchone()[0]

    def calculate_total_price(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT dbo.CalculateTotalPrice(%s)", [self.id])
            return cursor.fetchone()[0]
        
    class Meta:
        db_table = 'Flights'

    def __str__(self):
        return f"{self.departure_city} -> {self.arrival_city} ({self.departure_date})"
    
class City(models.Model):
    city_name = models.CharField(max_length=100)
    
    class Meta:
        db_table = 'city'

    def __str__(self):
        return self.city_name
    
class Customer(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name = 'customers')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    tc_number = models.CharField(max_length =11)
    email= models.EmailField()
    phone_number = models.CharField(max_length=15)
    selected_seat = models.CharField(max_length=10,blank=True, null=True)

    def get_full_name(self):
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT dbo.GetFullName(%s)", [self.id])
            return cursor.fetchone()[0]

    class Meta:
        db_table = 'customer'

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.flight.id}"
    
class FlightsBackup(models.Model): #trigger
    flight_id = models.IntegerField()
    departure_city = models.CharField(max_length=100)
    arrival_city = models.CharField(max_length=100)
    departure_date = models.DateField()
    backup_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'FlightsBackup'
        managed = False

class CustomerSeats(models.Model): #trigger
    flight_id = models.IntegerField()
    selected_seat = models.CharField(max_length=10)

    class Meta:
        db_table = 'CustomerSeats'
        managed = False

class FlightDetails(models.Model): #view
    flight_id = models.IntegerField()
    departure_city = models.CharField(max_length=100)
    arrival_city = models.CharField(max_length=100)
    departure_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    customer_first_name = models.CharField(max_length=100, null=True, blank=True)
    customer_last_name = models.CharField(max_length=100, null=True, blank=True)
    selected_seat = models.CharField(max_length=10, null=True, blank=True)

    class Meta:
        managed = False  # Django bu tabloyu yönetmeyecek
        db_table = 'vw_FlightDetails'