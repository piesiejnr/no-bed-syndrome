from django.urls import path
from . import views

app_name = 'admins'

urlpatterns = [
	path('', views.login_view, name='login'),
	path('logout/', views.logout_view, name='logout'),
	path('dashboard/', views.dashboard_view, name='dashboard'),
	path('beds/', views.bed_management_view, name='bed_management'),
	path('bookings/', views.booking_management_view, name='booking_management'),
	path('bookings/create/', views.create_booking_view, name='create_booking'),
	path('bookings/<uuid:booking_id>/confirm/', views.confirm_booking_view, name='confirm_booking'),
	path('bookings/<uuid:booking_id>/cancel/', views.cancel_booking_view, name='cancel_booking'),
	path('profile/', views.hospital_profile_view, name='hospital_profile'),
	path('logs/', views.activity_logs_view, name='activity_logs'),
	path('logs/clear/', views.clear_activity_logs_view, name='clear_activity_logs'),
]
