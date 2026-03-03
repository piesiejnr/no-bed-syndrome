from django.shortcuts import render, get_object_or_404
from .models import Hospital


def index(request):
	hospitals = Hospital.objects.all()[:10]
	return render(request, 'users/index.html', {'hospitals': hospitals})


def search(request):
	q = request.GET.get('q', '').strip()
	if q:
		hospitals = Hospital.objects.filter(name__icontains=q)[:50]
	else:
		hospitals = Hospital.objects.none()

	return render(request, 'users/search.html', {'hospitals': hospitals, 'query': q})


def nearby(request):
	# Placeholder: return all hospitals ordered by name.
	hospitals = Hospital.objects.all().order_by('name')
	return render(request, 'users/nearby.html', {'hospitals': hospitals})


def hospital_detail(request, pk):
	hospital = get_object_or_404(Hospital, pk=pk)
	reviews = hospital.reviews.all()
	avg_rating = None
	if reviews.exists():
		avg_rating = round(sum([r.rating for r in reviews]) / reviews.count(), 1)

	return render(request, 'users/hospital-detail.html', {
		'hospital_obj': hospital,
		'reviews': reviews,
		'avg_rating': avg_rating,
	})


def directions(request, pk):
	hospital = get_object_or_404(Hospital, pk=pk)
	return render(request, 'users/directions.html', {'hospital': hospital})

