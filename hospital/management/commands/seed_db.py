from django.core.management.base import BaseCommand
from django.db import transaction
from hospital.models import Hospital, BedInventory, Staff, Review, HospitalSetting, Booking, ActivityLog, HospitalAdmin
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Seed the database with sample hospitals, beds, staff, reviews, bookings, and activity logs.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding database...')

        with transaction.atomic():
            # Sample hospitals data
            hospitals_data = [
                {
                    'name': 'City General Hospital',
                    'description': 'A leading multi-specialty hospital providing comprehensive healthcare services with state-of-the-art facilities and experienced medical professionals.',
                    'address': 'Downtown Medical Center, 123 Main Street',
                    'phone': '(555) 123-4567',
                    'email': 'info@citygeneralhosp.com',
                    'website': 'https://www.citygeneralhosp.com',
                    'hours': '24/7',
                    'beds': {
                        'general': {'total': 120, 'available': 45, 'reserved': 0, 'status': 'available'},
                        'hdu': {'total': 40, 'available': 12, 'reserved': 0, 'status': 'available'},
                        'icu': {'total': 60, 'available': 8, 'reserved': 0, 'status': 'limited'},
                        'emergency': {'total': 30, 'available': 5, 'reserved': 0, 'status': 'limited'},
                    },
                    'staff': [
                        {'name': 'Dr. Sarah Johnson', 'title': 'Chief of Medicine'},
                        {'name': 'Dr. Michael Chen', 'title': 'Head of Surgery'},
                        {'name': 'Dr. Emily Rodriguez', 'title': 'Emergency Department Lead'},
                    ],
                    'reviews': [
                        {'author_name': 'John Doe', 'rating': 5, 'comment': 'Excellent service and caring staff'},
                        {'author_name': 'Jane Smith', 'rating': 4, 'comment': 'Very professional, quick response'},
                    ],
                },
                {
                    'name': 'Riverside Medical Center',
                    'description': 'A modern healthcare facility dedicated to providing quality medical services with focus on patient comfort and recovery.',
                    'address': 'Riverside Avenue, 456 Health Plaza',
                    'phone': '(555) 234-5678',
                    'email': 'contact@riversidemedical.com',
                    'website': 'https://www.riversidemedical.com',
                    'hours': '24/7',
                    'beds': {
                        'general': {'total': 100, 'available': 35, 'reserved': 0, 'status': 'available'},
                        'hdu': {'total': 35, 'available': 15, 'reserved': 0, 'status': 'available'},
                        'icu': {'total': 50, 'available': 22, 'reserved': 0, 'status': 'available'},
                        'emergency': {'total': 25, 'available': 3, 'reserved': 0, 'status': 'full'},
                    },
                    'staff': [
                        {'name': 'Dr. Robert Thompson', 'title': 'Hospital Director'},
                        {'name': 'Dr. Lisa Anderson', 'title': 'Head of Cardiology'},
                    ],
                    'reviews': [
                        {'author_name': 'Alice Brown', 'rating': 5, 'comment': 'Highly recommended'},
                    ],
                },
                {
                    'name': "St. Mary's Healthcare",
                    'description': 'Premier healthcare institution with advanced medical technology and compassionate care at the heart of our mission.',
                    'address': 'Medical Plaza, 789 Care Street',
                    'phone': '(555) 345-6789',
                    'email': 'admin@stmarys.com',
                    'website': 'https://www.stmarys.com',
                    'hours': '24/7',
                    'beds': {
                        'general': {'total': 150, 'available': 60, 'reserved': 0, 'status': 'available'},
                        'hdu': {'total': 45, 'available': 18, 'reserved': 0, 'status': 'available'},
                        'icu': {'total': 70, 'available': 30, 'reserved': 0, 'status': 'available'},
                        'emergency': {'total': 35, 'available': 10, 'reserved': 0, 'status': 'available'},
                    },
                    'staff': [
                        {'name': 'Dr. Patricia White', 'title': 'Chief Medical Officer'},
                    ],
                    'reviews': [
                        {'author_name': 'Michael Taylor', 'rating': 5, 'comment': 'Exceptional care and attention'},
                    ],
                },
                {
                    'name': 'North End Hospital',
                    'description': 'Community-focused medical center providing accessible healthcare services with specialized departments.',
                    'address': 'North District, 321 Medical Road',
                    'phone': '(555) 456-7890',
                    'email': 'support@northendhosp.com',
                    'website': 'https://www.northendhosp.com',
                    'hours': '24/7',
                    'beds': {
                        'general': {'total': 80, 'available': 25, 'reserved': 0, 'status': 'available'},
                        'hdu': {'total': 30, 'available': 8, 'reserved': 0, 'status': 'limited'},
                        'icu': {'total': 40, 'available': 5, 'reserved': 0, 'status': 'limited'},
                        'emergency': {'total': 20, 'available': 2, 'reserved': 0, 'status': 'full'},
                    },
                    'staff': [
                        {'name': 'Dr. William Harris', 'title': 'Hospital Administrator'},
                    ],
                    'reviews': [
                        {'author_name': 'Emma Wilson', 'rating': 4, 'comment': 'Good service, friendly staff'},
                    ],
                },
            ]

            for data in hospitals_data:
                hosp, created = Hospital.objects.get_or_create(
                    name=data['name'],
                    defaults={
                        'description': data['description'],
                        'address': data['address'],
                        'phone': data['phone'],
                        'email': data['email'],
                        'website': data['website'],
                        'hours': data.get('hours', '24/7'),
                    }
                )

                if created:
                    self.stdout.write(f'Created hospital: {hosp.name}')
                else:
                    self.stdout.write(f'Updating hospital: {hosp.name}')
                    hosp.description = data['description']
                    hosp.address = data['address']
                    hosp.phone = data['phone']
                    hosp.email = data['email']
                    hosp.website = data['website']
                    hosp.hours = data.get('hours', '24/7')
                    hosp.save()

                # Create/update beds
                for bed_key, bed_info in data['beds'].items():
                    bed_obj, _ = BedInventory.objects.update_or_create(
                        hospital=hosp,
                        bed_type=bed_key,
                        defaults={
                            'total': bed_info['total'],
                            'available': bed_info['available'],
                            'reserved': bed_info.get('reserved', 0),
                            'status': bed_info.get('status', 'available'),
                        }
                    )

                # Staff
                hosp.staff.all().delete()
                for s in data.get('staff', []):
                    Staff.objects.create(hospital=hosp, name=s['name'], title=s.get('title', ''), department=s.get('department', ''))

                # Reviews
                hosp.reviews.all().delete()
                for r in data.get('reviews', []):
                    Review.objects.create(hospital=hosp, author_name=r['author_name'], rating=r['rating'], comment=r.get('comment', ''))

                # Settings
                HospitalSetting.objects.update_or_create(
                    hospital=hosp,
                    defaults={
                        'reservation_duration': 45,
                        'allow_emergency_booking': True,
                        'require_min_beds': True,
                    }
                )

                # Create/update admin account
                admin_name = f'{hosp.name} Admin'
                admin_code = f'{hosp.id:04d}1234'  # Example: 00011234
                HospitalAdmin.objects.get_or_create(
                    hospital=hosp,
                    code=admin_code,
                    defaults={
                        'name': admin_name,
                        'is_active': True,
                    }
                )

            # Create sample bookings and activity logs
            hospitals = Hospital.objects.all()
            for hosp in hospitals:
                # Add 1-2 sample bookings
                for i in range(2):
                    bed_types = [b.bed_type for b in hosp.beds.all() if b.bed_type != 'emergency']
                    if not bed_types:
                        continue
                    bt = random.choice(bed_types)
                    booked_at = timezone.now()
                    expires_at = booked_at + timezone.timedelta(minutes=45)
                    booking = Booking.objects.create(
                        hospital=hosp,
                        name=f'Sample Patient {i+1}',
                        contact='(555) 000-0000',
                        bed_type=bt,
                        notes='Sample booking',
                        status=Booking.STATUS_ACTIVE,
                        booked_at=booked_at,
                        expires_at=expires_at,
                    )

                    # decrement availability/reserved if possible
                    try:
                        bed_inv = hosp.beds.get(bed_type=bt)
                        if bed_inv.available > 0:
                            bed_inv.available = max(0, bed_inv.available - 1)
                            bed_inv.reserved = bed_inv.reserved + 1
                            bed_inv.save()
                    except BedInventory.DoesNotExist:
                        pass

                    ActivityLog.objects.create(
                        hospital=hosp,
                        type=ActivityLog.TYPE_BOOKING,
                        description=f'Created sample booking {booking.id} for {booking.name}',
                        status=ActivityLog.STATUS_SUCCESS,
                    )

            self.stdout.write(self.style.SUCCESS('Seeding completed'))
