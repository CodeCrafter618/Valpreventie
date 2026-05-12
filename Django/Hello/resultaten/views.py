from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse
from home.models import Gemeente, Vragen

try:
    from weasyprint import HTML, CSS
    HAS_WEASYPRINT = True
except ImportError:
    HAS_WEASYPRINT = False

SESSION_KEY_VOLTOOID = 'vragenlijst_voltooid'
SESSION_KEY_ANTWOORDEN = 'vragenlijst_resultaat_antwoorden'


def _bepaal_beschrijving(score, totaal):
    if totaal == 0:
        return 'Er zijn geen vragen voor dit onderdeel.'

    if score == totaal:
        return 'Dit onderdeel gaat goed. U doet hier al de juiste dingen.'

    if score == 0:
        return 'Hier is nog veel winst te behalen. Bekijk wat u kunt verbeteren.'

    return 'Er zijn al goede stappen gezet, maar er is nog ruimte om dit verder te verbeteren.'


def _extract_tips_from_questions(questions):
    """Collect short tip lines from question.extra_info fields.

    Returns a short joined string suitable for the card description.
    """
    tips = []
    for q in questions:
        raw = (q.extra_info or "").strip()
        if not raw:
            continue
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        # prefer bullet lines after the first two lines; otherwise use the first line
        if len(lines) > 2:
            for line in lines[2:]:
                cleaned = line.lstrip('-• ').strip()
                if cleaned and cleaned not in tips:
                    tips.append(cleaned)
        else:
            cleaned = lines[0]
            if cleaned and cleaned not in tips:
                tips.append(cleaned)
    # Join a few short tips into one line separated by ' · '
    if not tips:
        return ""
    # Limit to max 3 tips to keep the card compact
    short = tips[:3]
    return ' · '.join(short)


def _extract_habits_from_questions(questions):
    """Collect the short habit titles from question.vraag fields.

    Returns a short joined string suitable for the card description.
    """
    habits = []
    for q in questions:
        title = (q.vraag or '').strip()
        if not title:
            continue
        if title not in habits:
            habits.append(title)
    if not habits:
        return ""
    # prefer the first 3 habit titles
    return ' · '.join(habits[:3])


def _bereken_score(antwoorden, vragen):
    totale_score = 0
    max_mogelijke_score = 0
    vragen_per_categorie = {}
    for vraag in vragen:
        cat = vraag.categorie or 'Overig'
        if cat not in vragen_per_categorie:
            vragen_per_categorie[cat] = {
                'vragen': [],
                'emoji': vraag.emoji or '📋',
                'score': 0,
                'totaal': 0,
                'aantal_vragen': 0,
            }
        vragen_per_categorie[cat]['vragen'].append(vraag)
        vragen_per_categorie[cat]['aantal_vragen'] += 1
        # Maximum score is max of ja or nee weging
        max_voor_vraag = max(vraag.weging, vraag.weging_nee)
        vragen_per_categorie[cat]['totaal'] += max_voor_vraag
        max_mogelijke_score += max_voor_vraag
    
    for cat, data in vragen_per_categorie.items():
        for vraag in data['vragen']:
            if str(vraag.id) in antwoorden:
                if antwoorden[str(vraag.id)]:
                    # Ja antwoord
                    data['score'] += vraag.weging
                    totale_score += vraag.weging
                else:
                    # Nee antwoord
                    data['score'] += vraag.weging_nee
                    totale_score += vraag.weging_nee

        data['toon_kans_op'] = data['score'] < data['totaal']
        # If the category is not fully good, prefer a description from the DB
        if data['score'] < data['totaal']:
            # Collect tip lines from questions' extra_info to show as tipbeschrijvingen
            # Prefer short habit titles (gewoontjes) instead of full question phrasing
            habit_text = _extract_habits_from_questions(data['vragen'])
            if habit_text:
                data['beschrijving'] = habit_text
            else:
                tip_text = _extract_tips_from_questions(data['vragen'])
                data['beschrijving'] = tip_text or _bepaal_beschrijving(data['score'], data['totaal'])
        else:
            data['beschrijving'] = _bepaal_beschrijving(data['score'], data['totaal'])
    
    return totale_score, vragen_per_categorie, max_mogelijke_score


def _bepaal_feedback(totale_score, max_mogelijke_score):
    """Bepaal feedback based on percentage of max possible score."""
    if max_mogelijke_score == 0:
        return 'laag', 'Er zijn geen vragen beschikbaar.', 'green'
    
    percentage = (totale_score / max_mogelijke_score) * 100
    
    if percentage >= 85:
        return 'laag', 'Goed bezig! U heeft een laag valrisico.', 'green'
    elif percentage >= 60:
        return 'gemiddeld', 'Er zijn verbeterpunten. Bekijk welke categorieën lager scoren.', 'orange'
    else:
        return 'hoog', 'Let op! U loopt een verhoogd risico. Het is raadzaam om actie te ondernemen of dit te bespreken met een professional.', 'red'


def resultaten(request):
    if not request.session.get(SESSION_KEY_VOLTOOID, False):
        return redirect('/vragen/')

    gemeente_zoekterm = (request.GET.get('gemeente') or '').strip()
    gevonden_gemeente = None
    gemeente_meldingen = []

    if gemeente_zoekterm:
        exacte_match = Gemeente.objects.filter(naam__iexact=gemeente_zoekterm).first()
        if exacte_match:
            gevonden_gemeente = exacte_match
        else:
            gevonden_gemeente = (
                Gemeente.objects.filter(Q(naam__icontains=gemeente_zoekterm)).order_by('naam').first()
            )

        if not gevonden_gemeente:
            gemeente_meldingen.append('Geen gemeente gevonden met deze naam.')
    
    opgeslagen = request.session.get(SESSION_KEY_ANTWOORDEN, {})
    if isinstance(opgeslagen, dict):
        antwoorden = {str(vraag_id): bool(antwoord) for vraag_id, antwoord in opgeslagen.items()}
    elif isinstance(opgeslagen, list):
        antwoorden = {}
        for antwoord in opgeslagen:
            if not isinstance(antwoord, dict):
                continue
            vraag_id = antwoord.get('vraag_id')
            if vraag_id is None:
                continue
            antwoorden[str(vraag_id)] = bool(antwoord.get('ja'))
    else:
        antwoorden = {}
    
    vragen = list(Vragen.objects.order_by('volgorde', 'id'))
    
    if not vragen:
        return render(request, 'resultaten/resultaten.html', {'heeft_vragen': False})
    
    totale_score, categoriescore, max_mogelijke_score = _bereken_score(antwoorden, vragen)
    risico, feedback, kleur = _bepaal_feedback(totale_score, max_mogelijke_score)
    
    feedback_dict = {
        'laag': {
            'titel': 'Goed bezig!',
            'tekst': 'U heeft een laag valrisico.',
            'kleur': 'success'
        },
        'gemiddeld': {
            'titel': 'Verbeterpunten',
            'tekst': 'Er zijn verbeterpunten. Bekijk welke categorieën lager scoren.',
            'kleur': 'warning'
        },
        'hoog': {
            'titel': 'Verhoogd risico',
            'tekst': 'Let op! U loopt een verhoogd risico. Het is raadzaam om actie te ondernemen.',
            'kleur': 'danger'
        }
    }
    
    context = {
        'heeft_vragen': True,
        'totale_score': totale_score,
        'max_score': len(vragen),
        'risico': risico,
        'feedback': feedback_dict[risico],
        'categoriescore': categoriescore,
        'antwoorden': antwoorden,
        'vragen': vragen,
        'gemeente_zoekterm': gemeente_zoekterm,
        'gevonden_gemeente': gevonden_gemeente,
        'gemeente_meldingen': gemeente_meldingen,
    }
    
    return render(request, 'resultaten/resultaten.html', context)


def pdf_download(request):
    """Generate and download PDF of results."""
    if not request.session.get(SESSION_KEY_VOLTOOID, False):
        return redirect('/vragen/')
    
    if not HAS_WEASYPRINT:
        return HttpResponse(
            'PDF generation library not installed. Please install weasyprint: pip install weasyprint',
            status=500
        )
    
    opgeslagen = request.session.get(SESSION_KEY_ANTWOORDEN, {})
    if isinstance(opgeslagen, dict):
        antwoorden = {str(vraag_id): bool(antwoord) for vraag_id, antwoord in opgeslagen.items()}
    elif isinstance(opgeslagen, list):
        antwoorden = {}
        for antwoord in opgeslagen:
            if not isinstance(antwoord, dict):
                continue
            vraag_id = antwoord.get('vraag_id')
            if vraag_id is None:
                continue
            antwoorden[str(vraag_id)] = bool(antwoord.get('ja'))
    else:
        antwoorden = {}
    
    vragen = list(Vragen.objects.order_by('volgorde', 'id'))
    
    if not vragen:
        return HttpResponse('No questions available', status=400)
    
    totale_score, categoriescore, max_mogelijke_score = _bereken_score(antwoorden, vragen)
    risico, feedback, kleur = _bepaal_feedback(totale_score, max_mogelijke_score)
    
    context = {
        'totale_score': totale_score,
        'max_score': len(vragen),
        'risico': risico,
        'categoriescore': categoriescore,
        'antwoorden': antwoorden,
        'vragen': vragen,
    }
    
    html_string = render(request, 'resultaten/pdf_template.html', context).content
    
    try:
        html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
        pdf = html.write_pdf()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="risicotest_resultaten.pdf"'
        return response
    except Exception as e:
        return HttpResponse(f'Error generating PDF: {str(e)}', status=500)
