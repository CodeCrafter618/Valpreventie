from django.shortcuts import render, redirect
from home.models import Vragen

SESSION_KEY_VOLTOOID = 'vragenlijst_voltooid'
SESSION_KEY_ANTWOORDEN = 'vragenlijst_resultaat_antwoorden'


def _bereken_score(antwoorden, vragen):
    totale_score = 0
    vragen_per_categorie = {}
    for vraag in vragen:
        cat = vraag.categorie or 'Overig'
        if cat not in vragen_per_categorie:
            vragen_per_categorie[cat] = {
                'vragen': [],
                'emoji': vraag.emoji or '📋',
                'score': 0,
                'totaal': 0,
            }
        vragen_per_categorie[cat]['vragen'].append(vraag)
        vragen_per_categorie[cat]['totaal'] += 1
    
    for cat, data in vragen_per_categorie.items():
        for vraag in data['vragen']:
            if str(vraag.id) in antwoorden and antwoorden[str(vraag.id)]:
                data['score'] += 1
                totale_score += 1
    
    return totale_score, vragen_per_categorie


def _bepaal_feedback(totale_score):
    if totale_score >= 12:
        return 'laag', 'Goed bezig! U heeft een laag valrisico.', 'green'
    elif totale_score >= 8:
        return 'gemiddeld', 'Er zijn verbeterpunten. Bekijk welke categorieën lager scoren.', 'orange'
    else:
        return 'hoog', 'Let op! U loopt een verhoogd risico. Het is raadzaam om actie te ondernemen of dit te bespreken met een professional.', 'red'


def resultaten(request):
    if not request.session.get(SESSION_KEY_VOLTOOID, False):
        return redirect('/vragen/')
    
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
    
    totale_score, categoriescore = _bereken_score(antwoorden, vragen)
    risico, feedback, kleur = _bepaal_feedback(totale_score)
    
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
    }
    
    return render(request, 'resultaten/resultaten.html', context)
