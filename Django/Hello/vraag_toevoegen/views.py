from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.db.models import Max

from home.models import Vragen
from home.categorie_herkenning import bepaal_standaard_meta


def _parse_int(value: str, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


@login_required(login_url="/login/")
def index(request):
    """Simple page to add a new vraag (question)."""
    if request.method == "POST":
        hoogste_volgorde = Vragen.objects.aggregate(max_volgorde=Max("volgorde"))["max_volgorde"] or 0
        vraagtekst = request.POST.get("vraag", "").strip()
        Vragen.objects.create(
            vraag=vraagtekst,
            extra_info=request.POST.get("extra_info", "").strip(),
            weging=_parse_int(request.POST.get("weging"), 0),
            weging_nee=_parse_int(request.POST.get("weging_nee"), 0),
            volgorde=_parse_int(request.POST.get("volgorde"), hoogste_volgorde + 1),
            categorie=bepaal_standaard_meta(vraagtekst)[0],
            emoji=bepaal_standaard_meta(vraagtekst)[1],
        )
        return redirect("/vragenlijstbeheer/")

    volgende = (Vragen.objects.aggregate(max_volgorde=Max("volgorde"))["max_volgorde"] or 0) + 1
    return render(request, "vraag_toevoegen/index.html", {"volgende_volgorde": volgende})
