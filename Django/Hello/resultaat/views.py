from django.shortcuts import redirect, render

from home.models import Antwoord


SESSION_KEY_VOLTOOID = "vragenlijst_voltooid"
SESSION_KEY_ANTWOORD_IDS = "vragenlijst_resultaat_antwoord_ids"


def _bepaal_advies(score: int, max_score: int) -> tuple[str, str]:
    if max_score <= 0:
        return "Onbekend", "Er is nog geen resultaat beschikbaar."

    percentage = round((score / max_score) * 100)

    if percentage >= 67:
        return (
            "Hoog risico",
            "Er zijn duidelijke aandachtspunten. Neem de adviezen uit de vragenlijst serieus en bespreek dit eventueel met een zorgverlener.",
        )
    if percentage >= 34:
        return (
            "Matig risico",
            "Er zijn enkele aandachtspunten. Let extra op en pas waar nodig je omgeving of gedrag aan.",
        )
    return (
        "Laag risico",
        "Je scoort gunstig op deze vragenlijst. Blijf alert op veranderingen in balans, zicht en omgeving.",
    )


def index(request):
    antwoord_ids = request.session.get(SESSION_KEY_ANTWOORD_IDS, [])
    if not antwoord_ids:
        return render(
            request,
            "resultaat/index.html",
            {
                "resultaat_beschikbaar": False,
            },
        )

    antwoorden = list(
        Antwoord.objects.filter(id__in=antwoord_ids).select_related("vraag")
    )
    if not antwoorden:
        request.session.pop(SESSION_KEY_VOLTOOID, None)
        request.session.pop(SESSION_KEY_ANTWOORD_IDS, None)
        return redirect("/vragen/")

    max_score = sum(antwoord.vraag.weging for antwoord in antwoorden)
    score = sum(antwoord.vraag.weging for antwoord in antwoorden if antwoord.ja_nee)
    advies_label, advies_tekst = _bepaal_advies(score, max_score)

    return render(
        request,
        "resultaat/index.html",
        {
            "resultaat_beschikbaar": True,
            "score": score,
            "max_score": max_score,
            "advies_label": advies_label,
            "advies_tekst": advies_tekst,
            "aantal_antwoorden": len(antwoorden),
        },
    )
