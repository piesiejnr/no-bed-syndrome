from django.urls import path
from . import views

app_name = 'hospital'

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('nearby/', views.nearby, name='nearby'),
    path('hospital/<int:pk>/', views.hospital_detail, name='hospital_detail'),
    path('directions/<int:pk>/', views.directions, name='directions'),
]
