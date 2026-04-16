from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="login"),
    path("uitloggen/", views.logout_view, name="logout"),
]
