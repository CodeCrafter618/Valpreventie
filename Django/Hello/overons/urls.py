from django.urls import path
from . import views

urlpatterns = [
    path('', views.overons, name='overons'),
]
