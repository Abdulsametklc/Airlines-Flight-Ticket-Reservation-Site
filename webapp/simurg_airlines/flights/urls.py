from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Ana sayfa
    path('search-flights/', views.flight_search, name='search-flights'),
    path('select-flight/', views.select_flight, name ='select-flight'),  # Uçuş arama
    path('customer-info/<int:flight_id>/', views.customer_info, name='customer-info'),
    path('seat-selection/<int:flight_id>/', views.seat_selection, name='seat-selection'),
    path('flight-details/', views.flight_details_view, name='flight-details'),
    path('admin-sql-functions/', views.admin_sql_functions, name='admin_sql_functions'),
    path('flight-function-details/', views.flight_function_details, name='flight_function_details'),
    path('authenticate-admin/', views.authenticate_admin, name='authenticate_admin'),
]