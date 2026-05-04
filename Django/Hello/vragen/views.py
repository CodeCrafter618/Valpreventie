from django.shortcuts import redirect, render

from home.models import Antwoord, Vragen


SESSION_KEY_VOLTOOID = "vragenlijst_voltooid"
SESSION_KEY_ANTWOORD_IDS = "vragenlijst_resultaat_antwoord_ids"


def _parse_index(raw_value: str, total: int) -> int:
    """Return a safe question index inside bounds."""
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        value = 0

    if total <= 0:
        return 0

    return max(0, min(value, total - 1))


def index(request):
    if request.GET.get("opnieuw") == "1":
        request.session.pop(SESSION_KEY_VOLTOOID, None)
        request.session.pop(SESSION_KEY_ANTWOORD_IDS, None)

    vragen_lijst = list(Vragen.objects.order_by("volgorde", "id"))
    totaal = len(vragen_lijst)

    if totaal == 0:
        return render(
            request,
            "vragen/vragen.html",
            {
                "heeft_vragen": False,
                "totaal": 0,
            },
        )

    huidige_index = _parse_index(request.GET.get("stap"), totaal)
    huidige_vraag = vragen_lijst[huidige_index]
    extra_info_regels = [
        regel.strip()
        for regel in (huidige_vraag.extra_info or "").splitlines()
        if regel.strip()
    ]
    extra_info_intro = extra_info_regels[0] if extra_info_regels else ""
    extra_info_subtitel = extra_info_regels[1] if len(extra_info_regels) > 1 else ""
    extra_info_punten = [
        regel.lstrip("-• ").strip()
        for regel in extra_info_regels[2:]
        if regel.lstrip("-• ").strip()
    ]

    if request.method == "POST":
        keuze = request.POST.get("keuze")
        if keuze in {"ja", "nee"}:
            antwoord = Antwoord.objects.create(vraag=huidige_vraag, ja_nee=keuze == "ja")

            antwoord_ids = request.session.get(SESSION_KEY_ANTWOORD_IDS, [])
            antwoord_ids.append(antwoord.id)
            request.session[SESSION_KEY_ANTWOORD_IDS] = antwoord_ids
            request.session.modified = True

            volgende = min(huidige_index + 1, totaal - 1)
            if huidige_index < totaal - 1:
                return redirect(f"/vragen/?stap={volgende}")

            request.session[SESSION_KEY_VOLTOOID] = True
            return redirect("/resultaat/")

    is_klaar = request.GET.get("klaar") == "1"
    voortgang = int(((huidige_index + 1) / totaal) * 100)

    return render(
        request,
        "vragen/vragen.html",
        {
            "heeft_vragen": True,
            "vraag": huidige_vraag,
            "extra_info_intro": extra_info_intro,
            "extra_info_subtitel": extra_info_subtitel,
            "extra_info_punten": extra_info_punten,
            "stap": huidige_index + 1,
            "totaal": totaal,
            "voortgang": voortgang,
            "kan_terug": huidige_index > 0,
            "terug_stap": huidige_index - 1,
            "is_laatste": huidige_index == totaal - 1,
            "is_klaar": is_klaar,
        },
    )
