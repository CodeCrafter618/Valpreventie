from django.shortcuts import redirect, render

from home.models import Vragen


SESSION_KEY_VOLTOOID = "vragenlijst_voltooid"
SESSION_KEY_ANTWOORDEN = "vragenlijst_resultaat_antwoorden"


def _parse_index(raw_value: str, total: int) -> int:
    """Return a safe question index inside bounds."""
    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        value = 0

    if total <= 0:
        return 0

    return max(0, min(value, total - 1))


def _haal_antwoorden_op(request) -> dict[str, bool]:
    opgeslagen = request.session.get(SESSION_KEY_ANTWOORDEN, {})
    if isinstance(opgeslagen, dict):
        return {str(vraag_id): bool(antwoord) for vraag_id, antwoord in opgeslagen.items()}

    if isinstance(opgeslagen, list):
        antwoorden = {}
        for antwoord in opgeslagen:
            if not isinstance(antwoord, dict):
                continue
            vraag_id = antwoord.get("vraag_id")
            if vraag_id is None:
                continue
            antwoorden[str(vraag_id)] = bool(antwoord.get("ja"))
        return antwoorden

    return {}


def index(request):
    if request.GET.get("opnieuw") == "1":
        request.session.pop(SESSION_KEY_VOLTOOID, None)
        request.session.pop(SESSION_KEY_ANTWOORDEN, None)

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
    foutmelding = ""
    antwoorden = _haal_antwoorden_op(request)

    if request.method == "POST":
        keuze = request.POST.get("keuze")
        if keuze in {"ja", "nee"}:
            antwoorden[str(huidige_vraag.id)] = keuze == "ja"
            request.session[SESSION_KEY_ANTWOORDEN] = antwoorden
            request.session.modified = True

            volgende = min(huidige_index + 1, totaal - 1)
            if huidige_index < totaal - 1:
                return redirect(f"/vragen/?stap={volgende}")

            request.session[SESSION_KEY_VOLTOOID] = True
            return redirect('/resultaten/')
        foutmelding = "Kies eerst JA of NEE om verder te gaan."

    is_klaar = request.GET.get("klaar") == "1"
    voortgang = int(((huidige_index + 1) / totaal) * 100)
    bestaand_antwoord = antwoorden.get(str(huidige_vraag.id))
    gekozen_keuze = ""
    if bestaand_antwoord is True:
        gekozen_keuze = "ja"
    elif bestaand_antwoord is False and str(huidige_vraag.id) in antwoorden:
        gekozen_keuze = "nee"

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
            "gekozen_keuze": gekozen_keuze,
            "foutmelding": foutmelding,
        },
    )
