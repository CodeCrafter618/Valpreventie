from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect, render

from home.models import Vragen


def _parse_int(value: str, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _standaard_meta(volgorde: int) -> tuple[str, str]:
    if volgorde <= 2:
        return "Controleer je ogen", "👁️"
    if volgorde <= 5:
        return "Maak het huis veilig", "🏠"
    if volgorde <= 7:
        return "Eet gezond", "🍎"
    if volgorde <= 9:
        return "Controleer je medicijnen", "💊"
    if volgorde <= 12:
        return "Beweeg voldoende", "🏃"
    return "Draag goede schoenen", "👟"


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
            categorie, emoji = _standaard_meta(vraag.volgorde)
            vraag.categorie = request.POST.get("categorie", "").strip() or categorie
            vraag.emoji = request.POST.get("emoji", "").strip() or emoji
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


def toevoegen(request):
    if request.method == "POST":
        hoogste_volgorde = Vragen.objects.aggregate(max_volgorde=Max("volgorde"))["max_volgorde"] or 0
        volgorde = _parse_int(request.POST.get("volgorde"), hoogste_volgorde + 1)
        categorie, emoji = _standaard_meta(volgorde)
        Vragen.objects.create(
            vraag=request.POST.get("vraag", "").strip(),
            extra_info=request.POST.get("extra_info", "").strip(),
            weging=0,
            volgorde=volgorde,
            categorie=request.POST.get("categorie", "").strip() or categorie,
            emoji=request.POST.get("emoji", "").strip() or emoji,
        )
        return redirect("/vragenlijstbeheer/")

    return render(
        request,
        "vragenlijstbeheer/toevoegen/index.html",
        {
            "volgende_volgorde": (Vragen.objects.aggregate(max_volgorde=Max("volgorde"))["max_volgorde"] or 0) + 1,
        },
    )
