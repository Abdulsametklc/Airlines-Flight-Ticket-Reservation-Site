from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from .models import Flight, City, Customer, FlightDetails
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.http import HttpResponseForbidden

def flight_function_details(request):
    customers = Customer.objects.all()
    flight_data = []

    for customer in customers:
        flight = Flight.objects.get(id=customer.flight_id)  # Müşteriyle ilişkili uçuşu al

        # CalculateFlightDuration fonksiyonunu çağır ve sonucu al
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT dbo.CalculateFlightDuration(%s, %s)",
                [flight.departure_time, flight.arrival_time]
            )
            duration = cursor.fetchone()[0]  # Sonuç alınır

        # CalculateTotalPrice fonksiyonunu çağır ve sonucu al
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT dbo.CalculateTotalPrice(%s, %s)",
                [flight.price, 1]  # Bu müşterinin fiyatı
            )
            total_price = cursor.fetchone()[0]  # Sonuç alınır

        # GetFullName fonksiyonunu çağır ve sonucu al
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT dbo.GetFullName(%s, %s)",
                [customer.first_name, customer.last_name]
            )
            full_name = cursor.fetchone()[0]  # Sonuç alınır

        # Müşteri ve uçuş verilerini listeye ekle
        flight_data.append({
            "full_name": full_name,
            "departure_city": flight.departure_city,
            "arrival_city": flight.arrival_city,
            "departure_date": flight.departure_date,
            "duration": duration,
            "total_price": total_price,
        })

    return render(request, "flights/function_details.html", {"flight_data": flight_data})

def authenticate_admin(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('flight_function_details')
        else:
            return HttpResponseForbidden("Invalid credentials or insufficient permissions.")
    return redirect('home')

def flight_details(request, flight_id):
    with connection.cursor() as cursor:
        # Uçuş Süresi Hesaplama
        cursor.execute("SELECT dbo.CalculateFlightDuration(%s, %s)", ['08:00:00', '10:30:00'])
        flight_duration = cursor.fetchone()[0]

        # Toplam Ücret Hesaplama
        cursor.execute("SELECT dbo.CalculateTotalPrice(%s, %s)", [150.00, 3])
        total_price = cursor.fetchone()[0]

        # Tam Ad
        cursor.execute("SELECT dbo.GetFullName(%s, %s)", ['Ahmet', 'Yılmaz'])
        full_name = cursor.fetchone()[0]

    return JsonResponse({
        "flight_duration": flight_duration,
        "total_price": total_price,
        "customer_name": full_name,
    })

@login_required
def admin_sql_functions(request):
    if not request.user.is_superuser:
        return redirect('admin:login')  # Admin olmayanları admin giriş sayfasına yönlendir.

    context = {}
    if request.method == "POST":
        function_name = request.POST.get('function_name')
        if function_name == "CalculateFlightDuration":
            with connection.cursor() as cursor:
                cursor.execute("SELECT dbo.CalculateFlightDuration(%s, %s)", ['08:00:00', '10:30:00'])
                result = cursor.fetchone()[0]
            context['result'] = f"Flight Duration: {result}"
        
        elif function_name == "CalculateTotalPrice":
            with connection.cursor() as cursor:
                cursor.execute("SELECT dbo.CalculateTotalPrice(%s, %s)", [150.00, 3])
                result = cursor.fetchone()[0]
            context['result'] = f"Total Price: {result}"
        
        elif function_name == "GetFullName":
            with connection.cursor() as cursor:
                cursor.execute("SELECT dbo.GetFullName(%s, %s)", ['Ahmet', 'Yılmaz'])
                result = cursor.fetchone()[0]
            context['result'] = f"Full Name: {result}"

    return render(request, 'flights/admin_sql_functions.html', context)

def flight_details_view(request):
    flight_details = FlightDetails.objects.all()
    return render(request, 'flights/flight_details.html', {'flight_details': flight_details})

def get_all_flights():
    with connection.cursor() as cursor:
        cursor.execute("EXEC GetAllFlights")
        return cursor.fetchall()

def index(request):
    return render(request, 'flights/index.html')

def home(request):
    # Flights tablosundaki unique kalkış, varış yerlerini ve tarihleri alıyoruz
    departure_cities = City.objects.all()
    arrival_cities = City.objects.all()
    passenger_counts = range(1, 5)  # Sabit bir aralık (1-4 yolcu)

    # Verileri şablona gönderiyoruz
    context = {
        'departure_cities': departure_cities,
        'arrival_cities': arrival_cities,
        'passenger_counts': passenger_counts,
    }
    return render(request, 'flights/home.html', context)

def list_triggers():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT name
            FROM sys.triggers
            WHERE parent_class_desc = 'OBJECT_OR_COLUMN'
        """)
        triggers = cursor.fetchall()
        print("Triggers in the database:")
        for trigger in triggers:
            print(trigger[0])

def update_customer_seat(customer_id, new_seat):
    customer = Customer.objects.get(id=customer_id)
    customer.selected_seat = new_seat
    customer.save()  # Trigger burada çalışır

def check_backup_table():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM FlightsBackup")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

def add_customer_with_trigger(flight_id, first_name, last_name, tc_number, email, phone_number, seat):
    with connection.cursor() as cursor:
        cursor.execute("""
            EXEC AddCustomerWithTrigger @FlightId = %s, @FirstName = %s, @LastName = %s,
            @TCNumber = %s, @Email = %s, @PhoneNumber = %s, @SelectedSeat = %s
        """, [flight_id, first_name, last_name, tc_number, email, phone_number, seat])

def flight_search(request):
    if request.method == 'GET':
        departure_city = request.GET.get('departure')
        arrival_city = request.GET.get('arrival')
        departure_date = request.GET.get('departure-date')

        flights = []
        # Veritabanında filtreleme
        with connection.cursor() as cursor:
            cursor.execute(
                "EXEC GetFlightsByCities @DepartureCity=%s, @ArrivalCity=%s, @DepartureDate=%s", 
                [departure_city, arrival_city, departure_date]
            )
            flights = cursor.fetchall()

        flights = [
            {
                'id': row[0],
                'departure_city': row[1],
                'arrival_city': row[2],
                'departure_date': row[3],
                'departure_time': row[4],
                'arrival_time': row[5],
                'price': row[6],
            }
            for row in flights
        ]

        # Sonuçları şablona gönder
        return render(request, 'flights/results.html', {'flights': flights})


def select_flight(request):
    if request.method == 'POST':
        flight_id = request.POST.get('flight_id')
        try:
            # Seçilen uçuşu veritabanından al
            flight = Flight.objects.get(id=flight_id)
            # Uçuş bilgilerini bir onay sayfasına yönlendirin
            return render(request, 'flights/seat_selection.html', {'flight': flight})
        except Flight.DoesNotExist:
            # Uçuş bulunamadıysa ana sayfaya yönlendir
            return redirect('home')
    return redirect('home')

def customer_info(request, flight_id):
    # Uçuş bilgilerini çek
    flight = get_object_or_404(Flight, id=flight_id)

    if request.method == 'POST':
        # Form verilerini alın
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        tc_number = request.POST.get('tc_number')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')

        print("Form Verileri:", first_name, last_name, tc_number, email, phone_number)
        # Tüm alanların dolu olduğunu kontrol edin
        if not all([first_name, last_name, tc_number, email, phone_number]):
            return render(request, 'flights/customer_info.html', {
                'flight': flight,
                'error': 'Tüm alanlar doldurulmalıdır.'
            })

        # Veritabanına kaydetmek için stored procedure çağır
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    EXEC AddCustomer @FlightId = %s, @FirstName = %s, @LastName = %s, @TCNumber = %s, @Email = %s, @PhoneNumber = %s""",
                    [flight_id, first_name, last_name, tc_number, email, phone_number]
                )
            print("Stored Procedure Başarıyla Çalıştı")
        except Exception as e:
            print("Hata Oluştu:", str(e))
            return render(request, 'flights/customer_info.html', {
                'flight': flight,
                'error': f'Hata: {str(e)}'
            })
        return redirect('seat-selection', flight_id=flight_id)
    else:
        print("GET Methodu çalıştı.")
    # GET isteği durumunda müşteri bilgi formunu göster
    return render(request, 'flights/customer_info.html', {'flight': flight})

def generate_seats():
    seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']
    rows = 150 // len(seat_letters)  # Sabit 150 koltuk
    return [f"{letter}{row}" for row in range(1, rows + 1) for letter in seat_letters]

def seat_selection(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)

    rows = [[f"{chr(65 + row)}{col + 1}" for col in range(10)] for row in range(15)]  # Koltuk düzeni

    if request.method == 'POST':
        selected_seat = request.POST.get('selected_seat')

        if not selected_seat:
            return render(request, 'flights/seat_selection.html', {
                'flight': flight,
                'rows': rows,
                'error': 'Bir koltuk seçmeniz gerekiyor.'
            })

        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    EXEC UpdateCustomerSeat @FlightId=%s, @SelectedSeat=%s
                    """, [flight_id, selected_seat]
                )
            # Başarılı işlem sonrası success sayfasına yönlendir
            return render(request, 'flights/success.html', {
                'flight': flight,
                'selected_seat': selected_seat,
            })
        except Exception as e:
            return render(request, 'flights/seat_selection.html', {
                'flight': flight,
                'rows': rows,
                'error': f'Hata oluştu: {str(e)}'
            })

    return render(request, 'flights/seat_selection.html', {
        'flight': flight,
        'rows': rows
    })
