from datetime import datetime

from django.http import HttpResponse
from django.shortcuts import redirect, render


SESSION_KEY_ANTWOORDEN = "vragenlijst_resultaat_antwoorden"


def _bepaal_advies(score: int) -> tuple[str, str]:
    if score >= 12:
        return "Goed bezig!", "U heeft een laag valrisico."
    if score >= 8:
        return "Er zijn verbeterpunten.", "Bekijk welke categorieen lager scoren."
    return (
        "Let op!",
        "U loopt een verhoogd risico. Het is raadzaam om actie te ondernemen of dit te bespreken met een professional.",
    )


def _punten_uitleg() -> str:
    return "Per Ja: 1 punt. Per Nee: 0 punten."


def _haal_antwoorden_uit_session(request) -> list[dict]:
    antwoorden = request.session.get(SESSION_KEY_ANTWOORDEN, [])
    if not isinstance(antwoorden, list):
        return []

    geldig = []
    for antwoord in antwoorden:
        if not isinstance(antwoord, dict):
            continue
        if "ja" not in antwoord:
            continue

        vraag_text = str(antwoord.get("vraag_text", "Vraag"))
        geldig.append(
            {
                "vraag_text": vraag_text,
                "ja": bool(antwoord.get("ja")),
            }
        )

    return geldig


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _build_simple_pdf(lines: list[str]) -> bytes:
    # Minimal PDF generator without external dependencies.
    y_start = 800
    line_height = 16
    text_commands = ["BT", "/F1 11 Tf", f"72 {y_start} Td"]

    for i, line in enumerate(lines):
        if i == 0:
            text_commands.append(f"({_pdf_escape(line)}) Tj")
        else:
            text_commands.append(f"0 -{line_height} Td")
            text_commands.append(f"({_pdf_escape(line)}) Tj")
    text_commands.append("ET")

    stream_data = "\n".join(text_commands).encode("latin-1", errors="replace")

    objects = []
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n")
    objects.append(
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>\nendobj\n"
    )
    objects.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    objects.append(
        b"5 0 obj\n<< /Length " + str(len(stream_data)).encode("ascii") + b" >>\nstream\n" + stream_data + b"\nendstream\nendobj\n"
    )

    pdf = bytearray()
    pdf.extend(b"%PDF-1.4\n")
    offsets = [0]

    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj)

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for off in offsets[1:]:
        pdf.extend(f"{off:010d} 00000 n \n".encode("ascii"))

    pdf.extend(
        (
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode("ascii")
    )

    return bytes(pdf)


def index(request):
    antwoorden = _haal_antwoorden_uit_session(request)
    if not antwoorden:
        return render(request, "resultaat/index.html", {"resultaat_beschikbaar": False})

    score = sum(1 for a in antwoorden if a["ja"])
    max_score = len(antwoorden)
    advies_label, advies_tekst = _bepaal_advies(score)

    return render(
        request,
        "resultaat/index.html",
        {
            "resultaat_beschikbaar": True,
            "score": score,
            "max_score": max_score,
            "advies_label": advies_label,
            "advies_tekst": advies_tekst,
            "punten_uitleg": _punten_uitleg(),
            "aantal_antwoorden": len(antwoorden),
            "antwoorden": antwoorden,
        },
    )


def download_pdf(request):
    antwoorden = _haal_antwoorden_uit_session(request)
    if not antwoorden:
        return redirect("resultaat:index")

    score = sum(1 for a in antwoorden if a["ja"])
    max_score = len(antwoorden)
    advies_label, advies_tekst = _bepaal_advies(score)

    lines = [
        "Valpreventie vragenlijst - resultaat",
        f"Datum: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
        "",
        f"Score: {score} van {max_score}",
        _punten_uitleg(),
        f"Advies: {advies_label}",
        advies_tekst,
        "",
        "Antwoorden:",
    ]

    for index_nr, antwoord in enumerate(antwoorden, start=1):
        antwoord_text = "Ja" if antwoord["ja"] else "Nee"
        lines.append(f"{index_nr}. {antwoord['vraag_text']} - {antwoord_text}")

    pdf_bytes = _build_simple_pdf(lines)
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="resultaat-valpreventie.pdf"'
    return response
