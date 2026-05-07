from io import BytesIO
from xml.sax.saxutils import escape
from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import redirect, render

from home.models import Antwoord


SESSION_KEY_VOLTOOID = "vragenlijst_voltooid"
SESSION_KEY_ANTWOORD_IDS = "vragenlijst_resultaat_antwoord_ids"


def _bepaal_advies_score(score: int) -> tuple[str, str]:
    """Return (label, tekst) using absolute score thresholds per spec."""
    if score >= 12:
        return ("Goed bezig!", "U heeft een laag valrisico.")
    if score >= 8:
        return ("Er zijn verbeterpunten.", "Bekijk welke categorieën lager scoren.")
    return (
        "Let op!",
        "U loopt een verhoogd risico. Het is raadzaam om actie te ondernemen of dit te bespreken met een professional.",
    )


def _haal_antwoorden_op(request):
    antwoord_ids = request.session.get(SESSION_KEY_ANTWOORD_IDS, [])
    if not antwoord_ids:
        return []

    antwoorden = list(
        Antwoord.objects.filter(id__in=antwoord_ids).select_related("vraag").order_by("vraag__volgorde", "id")
    )
    if not antwoorden:
        request.session.pop(SESSION_KEY_VOLTOOID, None)
        request.session.pop(SESSION_KEY_ANTWOORD_IDS, None)
        return []

    return antwoorden


def index(request):
    antwoorden = _haal_antwoorden_op(request)
    if not antwoorden:
        return render(request, "resultaat/index.html", {"resultaat_beschikbaar": False})

    # Score: each 'ja' is 1 point, 'nee' is 0
    score = sum(1 for a in antwoorden if a.ja_nee)
    max_score = len(antwoorden)
    advies_label, advies_tekst = _bepaal_advies_score(score)

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


def download_pdf(request):
    antwoorden = _haal_antwoorden_op(request)
    if not antwoorden:
        return redirect("resultaat:index")

    score = sum(1 for a in antwoorden if a.ja_nee)
    max_score = len(antwoorden)
    advies_label, advies_tekst = _bepaal_advies_score(score)

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except Exception:
        return HttpResponse(
            "ReportLab is not installed. Install it with 'pip install reportlab' to enable PDF download.",
            status=500,
        )

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm)
    styles = getSampleStyleSheet()

    story = []
    story.append(Paragraph("Valpreventie Vragenlijst - Resultaat", styles["Heading1"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f"Datum: {datetime.now().strftime('%d-%m-%Y %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(f"Score: {score} van {max_score} punten", styles["Heading2"]))
    story.append(Paragraph(escape(advies_label), styles["Heading3"]))
    story.append(Paragraph(escape(advies_tekst), styles["Normal"]))
    story.append(Spacer(1, 6 * mm))

    # Table of questions + answers
    table_data = [["Vraag", "Antwoord"]]
    for antwoord in antwoorden:
        table_data.append([antwoord.vraag.vraag, "Ja" if antwoord.ja_nee else "Nee"])

    table = Table(table_data, colWidths=[140 * mm, 30 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E5090")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    story.append(table)

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Valpreventie-Resultaat-{datetime.now().strftime("%Y%m%d")}.pdf"'
    response.write(pdf)
    return response
    """Genereer en download een PDF van de resultaten"""
    antwoord_ids = request.session.get(SESSION_KEY_ANTWOORD_IDS, [])
    if not antwoord_ids:
        return redirect("resultaat:index")

    antwoorden = list(
        Antwoord.objects.filter(id__in=antwoord_ids).select_related("vraag").order_by("vraag__volgorde")
    )
    
    if not antwoorden:
        return redirect("resultaat:index")

    # Berekening
    score = sum(1 for antwoord in antwoorden if antwoord.ja_nee)
    max_score = len(antwoorden)
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

    doc.build(story)
    return response
