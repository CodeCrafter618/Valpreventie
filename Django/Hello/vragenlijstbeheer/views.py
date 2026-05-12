from django.contrib.auth.decorators import login_required
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect, render

from home.models import Vragen
from home.categorie_herkenning import bepaal_standaard_meta


def _parse_int(value: str, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


@login_required(login_url="/login/")
def index(request):
    if request.method == "POST":
        actie = request.POST.get("actie")
        vraag_id = _parse_int(request.POST.get("vraag_id"), 0)

        vraag = get_object_or_404(Vragen, id=vraag_id)

        if actie == "verwijder":
            vraag.delete()
            return redirect("/vragenlijstbeheer/")

        if actie == "opslaan":
            vraag.vraag = request.POST.get("vraag", "").strip() or vraag.vraag
            vraag.extra_info = request.POST.get("extra_info", "").strip()
            vraag.volgorde = _parse_int(request.POST.get("volgorde"), vraag.volgorde)
            vraag.weging = _parse_int(request.POST.get("weging"), vraag.weging)
            vraag.weging_nee = _parse_int(request.POST.get("weging_nee"), vraag.weging_nee)
            vraag.categorie, vraag.emoji = bepaal_standaard_meta(vraag.vraag)
            vraag.save()
            return redirect("/vragenlijstbeheer/")

    edit_id = _parse_int(request.GET.get("edit"), 0)
    vragen = Vragen.objects.order_by("volgorde", "id")

    return render(
        request,
        "vragenlijstbeheer/index.html",
        {
            "vragen": vragen,
            "edit_id": edit_id,
        },
    )



