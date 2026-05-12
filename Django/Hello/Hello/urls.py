"""
URL configuration for Hello project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from resultaten.views import resultaten as resultaten_view, pdf_download

urlpatterns = [
    path('', include('home.urls')),
    path('login/', include('login.urls')),
    path('vragen/', include('vragen.urls')),
    path('resultaten/', resultaten_view, name='resultaten'),
    path('resultaten/pdf/', pdf_download, name='pdf_download'),
    path('vragenlijstbeheer/', include('vragenlijstbeheer.urls')),
    path('vraag-toevoegen/', include('vraag_toevoegen.urls')),
    path('overons/', include('overons.urls')),
    path('admin/', admin.site.urls),
]
