from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="vragenlijstbeheer"),
    path("toevoegen/", views.toevoegen, name="vragenlijstbeheer-toevoegen"),
]
