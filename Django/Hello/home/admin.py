from django.contrib import admin
from .models import Antwoord, Gemeente, Question, Vragen


@admin.register(Gemeente)
class GemeenteAdmin(admin.ModelAdmin):
	list_display = ("naam", "telefoonnummer", "adres")
	search_fields = ("naam", "telefoonnummer", "adres")


admin.site.register(Question)
admin.site.register(Vragen)
admin.site.register(Antwoord)
