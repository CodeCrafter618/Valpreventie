from __future__ import annotations

import re


_CATEGORIEN = [
    (
        "Controleer je ogen",
        "👁️",
        (
            "oog",
            "ogen",
            "opticien",
            "oogarts",
            "bril",
            "lenzen",
            "zicht",
        ),
    ),
    (
        "Maak het huis veilig",
        "🏠",
        (
            "vloer",
            "obstakel",
            "kleed",
            "drempel",
            "snoer",
            "kamer",
            "overloop",
            "badkamer",
            "verlichting",
            "lamp",
            "handgreep",
            "toilet",
            "douche",
            "huis",
        ),
    ),
    (
        "Eet gezond",
        "🍎",
        (
            "eet",
            "eiwit",
            "vlees",
            "vis",
            "zuivel",
            "eieren",
            "peulvruchten",
            "drink",
            "water",
            "vocht",
            "voeding",
        ),
    ),
    (
        "Controleer je medicijnen",
        "💊",
        (
            "medicijn",
            "medicijnen",
            "apotheker",
            "huisarts",
            "bijwerking",
            "duizelig",
            "slaperig",
        ),
    ),
    (
        "Beweeg voldoende",
        "🏃",
        (
            "beweeg",
            "bewegen",
            "wandelen",
            "fietsen",
            "tuinieren",
            "balans",
            "spier",
            "kracht",
            "oefening",
            "stoel",
            "opstaan",
        ),
    ),
    (
        "Draag goede schoenen",
        "👟",
        (
            "schoen",
            "schoenen",
            "slipper",
            "slippers",
            "pantoffel",
            "zool",
            "grip",
            "hiel",
            "sokken",
        ),
    ),
]

_DEFAULT_META = ("Algemeen", "❓")


def _normaliseer(tekst: str) -> str:
    return re.sub(r"\s+", " ", (tekst or "").strip().lower())


def bepaal_standaard_meta(vraagtekst: str) -> tuple[str, str]:
    tekst = _normaliseer(vraagtekst)
    if not tekst:
        return _DEFAULT_META

    for categorie, emoji, sleutelwoorden in _CATEGORIEN:
        if any(sleutelwoord in tekst for sleutelwoord in sleutelwoorden):
            return categorie, emoji

    return _DEFAULT_META
