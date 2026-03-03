from django.contrib import admin
from .models import (
	Hospital,
	BedInventory,
	Booking,
	Staff,
	ActivityLog,
	Review,
	HospitalSetting,
	HospitalAdmin as HospitalAdminModel,
)


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
	list_display = ('name', 'hospital_type', 'phone', 'email', 'created_at')
	search_fields = ('name', 'address', 'phone')
	list_filter = ('hospital_type',)


@admin.register(BedInventory)
class BedInventoryAdmin(admin.ModelAdmin):
	list_display = ('hospital', 'bed_type', 'total', 'available', 'reserved', 'status', 'booking_disabled')
	list_filter = ('bed_type', 'status')
	search_fields = ('hospital__name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	list_display = ('id', 'hospital', 'name', 'contact', 'bed_type', 'status', 'booked_at', 'expires_at')
	list_filter = ('status', 'bed_type')
	search_fields = ('name', 'contact')
	readonly_fields = ('id',)


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
	list_display = ('name', 'title', 'hospital', 'department', 'is_key_staff')
	list_filter = ('department', 'is_key_staff')
	search_fields = ('name', 'title')


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
	list_display = ('timestamp', 'hospital', 'type', 'status')
	list_filter = ('type', 'status', 'hospital')
	search_fields = ('description',)
	readonly_fields = ('timestamp',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
	list_display = ('author_name', 'hospital', 'rating', 'created_at')
	list_filter = ('rating',)
	search_fields = ('author_name', 'comment')


@admin.register(HospitalSetting)
class HospitalSettingAdmin(admin.ModelAdmin):
	list_display = ('hospital', 'reservation_duration', 'allow_emergency_booking', 'require_min_beds')


@admin.register(HospitalAdminModel)
class HospitalAdminAdmin(admin.ModelAdmin):
	list_display = ('name', 'hospital', 'code', 'is_active', 'created_at')
	list_filter = ('is_active', 'hospital')
	search_fields = ('name', 'code', 'hospital__name')
	readonly_fields = ('created_at', 'updated_at')
	fieldsets = (
		('Admin Info', {
			'fields': ('hospital', 'name', 'code', 'is_active')
		}),
		('Timestamps', {
			'fields': ('created_at', 'updated_at'),
			'classes': ('collapse',)
		}),
	)
