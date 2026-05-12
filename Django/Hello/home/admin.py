from django.contrib import admin
from .models import Antwoord, Gemeente, Question, Resultaat, Vragen


@admin.register(Gemeente)
class GemeenteAdmin(admin.ModelAdmin):
	list_display = ("naam", "telefoonnummer", "adres")
	search_fields = ("naam", "telefoonnummer", "adres")


admin.site.register(Question)
admin.site.register(Vragen)


class AntwoordInline(admin.TabularInline):
	model = Antwoord
	extra = 0
	fields = ("vraag", "ja_nee", "behaalde_score", "aangemaakt_op")
	readonly_fields = ("vraag", "ja_nee", "behaalde_score", "aangemaakt_op")
	can_delete = False


@admin.register(Resultaat)
class ResultaatAdmin(admin.ModelAdmin):
	list_display = ("id", "risico", "totale_score", "max_score", "gemeente_zoekterm", "aangemaakt_op")
	search_fields = ("gemeente_zoekterm", "sessie_key", "risico")
	list_filter = ("risico", "aangemaakt_op")
	inlines = [AntwoordInline]


admin.site.register(Antwoord)
