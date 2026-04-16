from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from home.models import Vragen


def _parse_int(value: str, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


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
            vraag.weging = _parse_int(request.POST.get("weging"), vraag.weging)
            vraag.volgorde = _parse_int(request.POST.get("volgorde"), vraag.volgorde)
            vraag.save()
            return redirect("/vragenlijstbeheer/")

    edit_id = _parse_int(request.GET.get("edit"), 0)

    vragen = (
        Vragen.objects.order_by("volgorde", "id")
        .annotate(
            ja_totaal=Count("antwoorden", filter=Q(antwoorden__ja_nee=True)),
            nee_totaal=Count("antwoorden", filter=Q(antwoorden__ja_nee=False)),
        )
    )

    return render(
        request,
        "vragenlijstbeheer/index.html",
        {
            "vragen": vragen,
            "edit_id": edit_id,
        },
    )
