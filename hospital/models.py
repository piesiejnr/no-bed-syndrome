from django.conf import settings
from django.db import models
from django.utils import timezone
import uuid


class Hospital(models.Model):
	name = models.CharField(max_length=200)
	hospital_type = models.CharField(max_length=100, blank=True)
	description = models.TextField(blank=True)
	phone = models.CharField(max_length=30, blank=True)
	emergency_phone = models.CharField(max_length=30, blank=True)
	email = models.EmailField(blank=True)
	address = models.TextField(blank=True)
	website = models.URLField(blank=True)
	hours = models.CharField(max_length=50, blank=True, default='24/7')
	latitude = models.FloatField(null=True, blank=True)
	longitude = models.FloatField(null=True, blank=True)
	main_image = models.URLField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.name


class BedInventory(models.Model):
	BED_GENERAL = 'general'
	BED_HDU = 'hdu'
	BED_ICU = 'icu'
	BED_EMERGENCY = 'emergency'

	BED_TYPE_CHOICES = [
		(BED_GENERAL, 'General Ward'),
		(BED_HDU, 'HDU'),
		(BED_ICU, 'ICU'),
		(BED_EMERGENCY, 'Emergency'),
	]

	STATUS_AVAILABLE = 'available'
	STATUS_LIMITED = 'limited'
	STATUS_FULL = 'full'

	STATUS_CHOICES = [
		(STATUS_AVAILABLE, 'Available'),
		(STATUS_LIMITED, 'Limited'),
		(STATUS_FULL, 'Full'),
	]

	hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='beds')
	bed_type = models.CharField(max_length=20, choices=BED_TYPE_CHOICES)
	total = models.PositiveIntegerField(default=0)
	available = models.PositiveIntegerField(default=0)
	reserved = models.PositiveIntegerField(default=0)
	booking_disabled = models.BooleanField(default=False)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)

	class Meta:
		unique_together = ('hospital', 'bed_type')
		ordering = ['hospital', 'bed_type']

	def __str__(self):
		return f"{self.hospital.name} - {self.get_bed_type_display()}"

	@property
	def occupied(self):
		occ = self.total - self.available - self.reserved
		return max(0, occ)

	@property
	def utilization_percent(self):
		if self.total <= 0:
			return 0
		return round((self.occupied / self.total) * 100)


class Booking(models.Model):
	STATUS_ACTIVE = 'active'
	STATUS_CONFIRMED = 'confirmed'
	STATUS_EXPIRED = 'expired'
	STATUS_CANCELLED = 'cancelled'

	STATUS_CHOICES = [
		(STATUS_ACTIVE, 'Active'),
		(STATUS_CONFIRMED, 'Confirmed'),
		(STATUS_EXPIRED, 'Expired'),
		(STATUS_CANCELLED, 'Cancelled'),
	]

	id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
	hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='bookings')
	name = models.CharField(max_length=200)
	contact = models.CharField(max_length=100)
	bed_type = models.CharField(max_length=20, choices=BedInventory.BED_TYPE_CHOICES)
	notes = models.TextField(blank=True)
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
	booked_at = models.DateTimeField(default=timezone.now)
	expires_at = models.DateTimeField(null=True, blank=True)
	created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	cancelled_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ['-booked_at']
		indexes = [models.Index(fields=['expires_at']), models.Index(fields=['status'])]

	def __str__(self):
		return f"Booking {self.id} - {self.name} ({self.get_status_display()})"


class Staff(models.Model):
	hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='staff')
	name = models.CharField(max_length=200)
	title = models.CharField(max_length=200, blank=True)
	department = models.CharField(max_length=200, blank=True)
	contact = models.CharField(max_length=200, blank=True)
	is_key_staff = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.name} — {self.title or 'Staff'}"


class ActivityLog(models.Model):
	TYPE_BED = 'bed'
	TYPE_BOOKING = 'booking'
	TYPE_PROFILE = 'profile'
	TYPE_STAFF = 'staff'
	TYPE_LOGIN = 'login'
	TYPE_EMERGENCY = 'emergency'
	TYPE_OTHER = 'other'

	TYPE_CHOICES = [
		(TYPE_BED, 'Bed Management'),
		(TYPE_BOOKING, 'Booking'),
		(TYPE_PROFILE, 'Profile Update'),
		(TYPE_STAFF, 'Staff Management'),
		(TYPE_LOGIN, 'Login/Logout'),
		(TYPE_EMERGENCY, 'Emergency'),
		(TYPE_OTHER, 'Other'),
	]

	STATUS_SUCCESS = 'success'
	STATUS_WARNING = 'warning'
	STATUS_ERROR = 'error'

	STATUS_CHOICES = [
		(STATUS_SUCCESS, 'Success'),
		(STATUS_WARNING, 'Warning'),
		(STATUS_ERROR, 'Error'),
	]

	hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='activity_logs')
	timestamp = models.DateTimeField(auto_now_add=True)
	type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_OTHER)
	description = models.TextField()
	status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUCCESS)
	user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
	metadata = models.JSONField(null=True, blank=True)

	class Meta:
		ordering = ['-timestamp']

	def __str__(self):
		return f"[{self.timestamp}] {self.get_type_display()} — {self.status}"


class Review(models.Model):
	hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='reviews')
	author_name = models.CharField(max_length=200)
	rating = models.PositiveSmallIntegerField()
	comment = models.TextField(blank=True)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ['-created_at']

	def __str__(self):
		return f"{self.author_name} — {self.rating}/5"


class HospitalSetting(models.Model):
	hospital = models.OneToOneField(Hospital, on_delete=models.CASCADE, related_name='settings')
	reservation_duration = models.PositiveIntegerField(default=45, help_text='Reservation duration in minutes')
	allow_emergency_booking = models.BooleanField(default=True)
	require_min_beds = models.BooleanField(default=True)
	extra = models.JSONField(null=True, blank=True)

	def __str__(self):
		return f"Settings for {self.hospital.name}"


class HospitalAdmin(models.Model):
	hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='admins')
	name = models.CharField(max_length=200)
	code = models.CharField(max_length=50, unique=True, help_text='Admin login code')
	is_active = models.BooleanField(default=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		unique_together = ('hospital', 'code')

	def __str__(self):
		return f"{self.name} - {self.hospital.name}"

