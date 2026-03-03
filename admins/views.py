from datetime import timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.db.models import Sum, Avg, F
from django.http import JsonResponse
from django.utils import timezone
from hospital.models import Hospital, HospitalAdmin, BedInventory, Booking, Staff, Review, ActivityLog


@require_http_methods(['GET', 'POST'])
def login_view(request):
	if request.method == 'POST':
		hospital_id = request.POST.get('hospital')
		code = request.POST.get('code')

		try:
			hospital = Hospital.objects.get(id=hospital_id)
			admin = HospitalAdmin.objects.get(hospital=hospital, code=code, is_active=True)
			
			# Store in session
			request.session['admin_id'] = admin.id
			request.session['hospital_id'] = hospital.id
			request.session['admin_name'] = admin.name
			
			return redirect('admins:dashboard')
		except (Hospital.DoesNotExist, HospitalAdmin.DoesNotExist):
			messages.error(request, 'Invalid hospital or code')
	
	hospitals = Hospital.objects.all()
	return render(request, 'admins/login.html', {'hospitals': hospitals})


def logout_view(request):
	request.session.flush()
	return redirect('admins:login')


def dashboard_view(request):
	if 'hospital_id' not in request.session:
		return redirect('admins:login')
	
	hospital_id = request.session['hospital_id']
	hospital = Hospital.objects.get(id=hospital_id)
	beds_qs = BedInventory.objects.filter(hospital=hospital)
	bookings_qs = Booking.objects.filter(hospital=hospital).order_by('-booked_at')
	staff_qs = Staff.objects.filter(hospital=hospital)
	reviews_qs = Review.objects.filter(hospital=hospital)

	total_beds = beds_qs.aggregate(total=Sum('total'))['total'] or 0
	active_bookings_count = bookings_qs.filter(status='active').count()
	staff_count = staff_qs.count()
	avg_rating_val = reviews_qs.aggregate(avg=Avg('rating'))['avg']
	avg_rating = round(avg_rating_val, 1) if avg_rating_val is not None else None

	context = {
		'hospital': hospital,
		'beds': beds_qs,
		'bookings': bookings_qs.filter(status='active'),
		'bookings_recent': bookings_qs[:10],
		'staff': staff_qs,
		'reviews': reviews_qs.order_by('-created_at'),
		'activity_logs': ActivityLog.objects.filter(hospital=hospital).order_by('-timestamp')[:10],
		'total_beds': total_beds,
		'booking_count': active_bookings_count,
		'staff_count': staff_count,
		'avg_rating': avg_rating,
	}
	return render(request, 'admins/dashboard.html', context)


@require_http_methods(['GET', 'POST'])
def bed_management_view(request):
	if 'hospital_id' not in request.session:
		return redirect('admins:login')

	hospital_id = request.session['hospital_id']
	hospital = Hospital.objects.get(id=hospital_id)

	if request.method == 'POST':
		action = request.POST.get('action')
		bed_type = request.POST.get('bed_type')

		if action == 'update_bed':
			try:
				total = int(request.POST.get('total', 0))
				available = int(request.POST.get('available', 0))
				reserved = int(request.POST.get('reserved', 0))
			except (TypeError, ValueError):
				messages.error(request, 'Invalid bed values.')
				return redirect('admins:bed_management')

			if total < 0 or available < 0 or reserved < 0:
				messages.error(request, 'Bed values cannot be negative.')
				return redirect('admins:bed_management')

			if available + reserved > total:
				messages.error(request, 'Available + Reserved cannot exceed Total beds.')
				return redirect('admins:bed_management')

			bed, _ = BedInventory.objects.get_or_create(hospital=hospital, bed_type=bed_type)
			bed.total = total
			bed.available = available
			bed.reserved = reserved
			bed.save()

			ActivityLog.objects.create(
				hospital=hospital,
				type=ActivityLog.TYPE_BED,
				description=f'Updated {bed.get_bed_type_display()} bed counts',
				status=ActivityLog.STATUS_SUCCESS,
			)
			messages.success(request, 'Bed counts updated successfully.')

		elif action == 'reset_bed':
			defaults = {
				BedInventory.BED_GENERAL: {'total': 120, 'available': 45, 'reserved': 0},
				BedInventory.BED_HDU: {'total': 40, 'available': 12, 'reserved': 0},
				BedInventory.BED_ICU: {'total': 60, 'available': 8, 'reserved': 0},
				BedInventory.BED_EMERGENCY: {'total': 30, 'available': 5, 'reserved': 0},
			}
			if bed_type in defaults:
				bed, _ = BedInventory.objects.get_or_create(hospital=hospital, bed_type=bed_type)
				bed.total = defaults[bed_type]['total']
				bed.available = defaults[bed_type]['available']
				bed.reserved = defaults[bed_type]['reserved']
				bed.save()

				ActivityLog.objects.create(
					hospital=hospital,
					type=ActivityLog.TYPE_BED,
					description=f'Reset {bed.get_bed_type_display()} beds to defaults',
					status=ActivityLog.STATUS_WARNING,
				)
				messages.success(request, 'Bed counts reset to defaults.')

		elif action == 'release_all':
			BedInventory.objects.filter(hospital=hospital).update(reserved=0, available=F('total'))
			ActivityLog.objects.create(
				hospital=hospital,
				type=ActivityLog.TYPE_EMERGENCY,
				description='Emergency: Released all reserved beds',
				status=ActivityLog.STATUS_WARNING,
			)
			messages.success(request, 'All reserved beds released.')

		elif action == 'toggle_booking' and bed_type:
			bed = get_object_or_404(BedInventory, hospital=hospital, bed_type=bed_type)
			bed.booking_disabled = not bed.booking_disabled
			bed.save()

			ActivityLog.objects.create(
				hospital=hospital,
				type=ActivityLog.TYPE_BED,
				description=f'Toggled booking for {bed.get_bed_type_display()}',
				status=ActivityLog.STATUS_WARNING,
			)
			messages.success(request, 'Booking availability updated.')

		return redirect('admins:bed_management')

	beds = BedInventory.objects.filter(hospital=hospital)

	context = {
		'hospital': hospital,
		'beds': beds,
	}
	return render(request, 'admins/bed-management.html', context)


def booking_management_view(request):
	if 'hospital_id' not in request.session:
		return redirect('admins:login')
	
	hospital_id = request.session['hospital_id']
	hospital = Hospital.objects.get(id=hospital_id)
	bookings = Booking.objects.filter(hospital=hospital).order_by('-booked_at')
	
	# reservation duration default to 45 if not configured
	try:
		reservation_duration = hospital.settings.reservation_duration
	except Exception:
		reservation_duration = 45

	context = {
		'hospital': hospital,
		'bookings': bookings,
		'reservation_duration': reservation_duration,
	}
	return render(request, 'admins/booking-management.html', context)


@require_http_methods(['POST'])
def create_booking_view(request):
	if 'hospital_id' not in request.session:
		return redirect('admins:login')

	hospital_id = request.session['hospital_id']
	hospital = get_object_or_404(Hospital, id=hospital_id)

	name = request.POST.get('name', '').strip()
	contact = request.POST.get('contact', '').strip()
	bed_type = request.POST.get('bed_type', '').strip()
	notes = request.POST.get('notes', '').strip()

	if not name or not contact or not bed_type:
		messages.error(request, 'Name, contact, and bed type are required.')
		return redirect('admins:booking_management')

	bed_inv = BedInventory.objects.filter(hospital=hospital, bed_type=bed_type).first()
	if not bed_inv:
		messages.error(request, 'Selected bed type is not configured.')
		return redirect('admins:booking_management')

	if bed_inv.booking_disabled:
		messages.error(request, 'Bookings are disabled for this bed type.')
		return redirect('admins:booking_management')

	if bed_inv.available <= 0:
		messages.error(request, 'No available beds for the selected type.')
		return redirect('admins:booking_management')

	try:
		reservation_duration = hospital.settings.reservation_duration
	except Exception:
		reservation_duration = 45

	with transaction.atomic():
		booking = Booking.objects.create(
			hospital=hospital,
			name=name,
			contact=contact,
			bed_type=bed_type,
			notes=notes,
			expires_at=timezone.now() + timedelta(minutes=reservation_duration),
		)

		bed_inv.reserved = max(0, bed_inv.reserved + 1)
		bed_inv.available = max(0, bed_inv.available - 1)
		bed_inv.save()

		ActivityLog.objects.create(
			hospital=hospital,
			type=ActivityLog.TYPE_BOOKING,
			description=f'Created booking #{booking.id} by admin {request.session.get("admin_name")}',
			status=ActivityLog.STATUS_SUCCESS,
		)

	messages.success(request, 'Booking created successfully.')
	return redirect('admins:booking_management')


@require_http_methods(['POST'])
def confirm_booking_view(request, booking_id):
	if 'hospital_id' not in request.session:
		return JsonResponse({'ok': False, 'error': 'Not authenticated'}, status=403)

	hospital_id = request.session['hospital_id']
	hospital = get_object_or_404(Hospital, id=hospital_id)
	booking = get_object_or_404(Booking, pk=booking_id, hospital=hospital)

	booking.status = Booking.STATUS_CONFIRMED
	booking.save()

	ActivityLog.objects.create(hospital=hospital, type=ActivityLog.TYPE_BOOKING,
							   description=f'Confirmed booking #{booking.id} by admin {request.session.get("admin_name")}',
							   status=ActivityLog.STATUS_SUCCESS)

	return JsonResponse({'ok': True, 'status': booking.status})


@require_http_methods(['POST'])
def cancel_booking_view(request, booking_id):
	if 'hospital_id' not in request.session:
		return JsonResponse({'ok': False, 'error': 'Not authenticated'}, status=403)

	hospital_id = request.session['hospital_id']
	hospital = get_object_or_404(Hospital, id=hospital_id)
	booking = get_object_or_404(Booking, pk=booking_id, hospital=hospital)

	# Update bed inventory: release reserved and increase available
	try:
		bed_inv = BedInventory.objects.get(hospital=hospital, bed_type=booking.bed_type)
		# adjust counts safely
		if bed_inv.reserved > 0:
			bed_inv.reserved = max(0, bed_inv.reserved - 1)
		bed_inv.available = min(bed_inv.total, bed_inv.available + 1)
		bed_inv.save()
	except BedInventory.DoesNotExist:
		bed_inv = None

	booking.status = Booking.STATUS_CANCELLED
	booking.cancelled_at = timezone.now()
	booking.save()

	ActivityLog.objects.create(hospital=hospital, type=ActivityLog.TYPE_BOOKING,
							   description=f'Cancelled booking #{booking.id} by admin {request.session.get("admin_name")}',
							   status=ActivityLog.STATUS_WARNING)

	return JsonResponse({'ok': True, 'status': booking.status})


def hospital_profile_view(request):
	if 'hospital_id' not in request.session:
		return redirect('admins:login')
	
	hospital_id = request.session['hospital_id']
	hospital = Hospital.objects.get(id=hospital_id)
	
	if request.method == 'POST':
		hospital.name = request.POST.get('name', hospital.name)
		hospital.description = request.POST.get('description', hospital.description)
		hospital.address = request.POST.get('address', hospital.address)
		hospital.phone = request.POST.get('phone', hospital.phone)
		hospital.email = request.POST.get('email', hospital.email)
		hospital.emergency_phone = request.POST.get('emergency_phone', hospital.emergency_phone)
		hospital.website = request.POST.get('website', hospital.website)
		hospital.hours = request.POST.get('hours', hospital.hours)
		hospital.save()
		messages.success(request, 'Hospital profile updated successfully')
		return redirect('admins:hospital_profile')
	
	context = {
		'hospital': hospital,
	}
	return render(request, 'admins/hospital-profile.html', context)


def activity_logs_view(request):
	if 'hospital_id' not in request.session:
		return redirect('admins:login')
	
	hospital_id = request.session['hospital_id']
	hospital = Hospital.objects.get(id=hospital_id)
	logs = ActivityLog.objects.filter(hospital=hospital).order_by('-timestamp')
	
	context = {
		'hospital': hospital,
		'logs': logs,
	}
	return render(request, 'admins/activity-logs.html', context)


@require_http_methods(['POST'])
def clear_activity_logs_view(request):
	if 'hospital_id' not in request.session:
		return redirect('admins:login')

	hospital_id = request.session['hospital_id']
	hospital = get_object_or_404(Hospital, id=hospital_id)

	ActivityLog.objects.filter(hospital=hospital).delete()
	ActivityLog.objects.create(
		hospital=hospital,
		type=ActivityLog.TYPE_OTHER,
		description='Cleared all activity logs',
		status=ActivityLog.STATUS_WARNING,
	)

	messages.success(request, 'Activity logs cleared.')
	return redirect('admins:activity_logs')
