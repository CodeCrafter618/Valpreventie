from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from home.models import Antwoord, Gemeente, Resultaat, Vragen

SESSION_KEY_VOLTOOID = 'vragenlijst_voltooid'
SESSION_KEY_ANTWOORDEN = 'vragenlijst_resultaat_antwoorden'
SESSION_KEY_RESULTAAT_ID = 'vragenlijst_resultaat_id'


def _haal_antwoorden_op(opgeslagen):
    if isinstance(opgeslagen, dict):
        return {str(vraag_id): bool(antwoord) for vraag_id, antwoord in opgeslagen.items()}

    if isinstance(opgeslagen, list):
        antwoorden = {}
        for antwoord in opgeslagen:
            if not isinstance(antwoord, dict):
                continue
            vraag_id = antwoord.get('vraag_id')
            if vraag_id is None:
                continue
            antwoorden[str(vraag_id)] = bool(antwoord.get('ja'))
        return antwoorden

    return {}


def _zoek_gemeente(gemeente_zoekterm):
    if not gemeente_zoekterm:
        return None, []

    meldingen = []
    exacte_match = Gemeente.objects.filter(naam__iexact=gemeente_zoekterm).first()
    if exacte_match:
        return exacte_match, meldingen

    gevonden = Gemeente.objects.filter(Q(naam__icontains=gemeente_zoekterm)).order_by('naam').first()
    if not gevonden:
        meldingen.append('Geen gemeente gevonden met deze naam.')
    return gevonden, meldingen


def _sla_resultaat_op(request, gemeente_zoekterm, gevonden_gemeente, vragen, antwoorden, totale_score, max_mogelijke_score, risico):
    if not request.session.session_key:
        request.session.save()

    with transaction.atomic():
        resultaat = Resultaat.objects.create(
            sessie_key=request.session.session_key or '',
            gemeente_zoekterm=gemeente_zoekterm,
            gemeente=gevonden_gemeente,
            totale_score=totale_score,
            max_score=max_mogelijke_score,
            risico=risico,
        )

        for vraag in vragen:
            ja_antwoord = bool(antwoorden.get(str(vraag.id), False))
            Antwoord.objects.create(
                resultaat=resultaat,
                vraag=vraag,
                ja_nee=ja_antwoord,
                behaalde_score=vraag.weging if ja_antwoord else vraag.weging_nee,
            )

    return resultaat
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

    if not request.session.session_key:
        request.session.save()

    gemeente_zoekterm = (request.GET.get('gemeente') or '').strip()
    gevonden_gemeente, gemeente_meldingen = _zoek_gemeente(gemeente_zoekterm)
    
    opgeslagen = request.session.get(SESSION_KEY_ANTWOORDEN, {})
    antwoorden = _haal_antwoorden_op(opgeslagen)
    
    vragen = list(Vragen.objects.order_by('volgorde', 'id'))
    
    if not vragen:
        return render(request, 'resultaten/resultaten.html', {'heeft_vragen': False})
    
    totale_score, categoriescore, max_mogelijke_score = _bereken_score(antwoorden, vragen)
    risico, feedback, kleur = _bepaal_feedback(totale_score, max_mogelijke_score)

    # Controleer of we al een resultaat hebben voor deze sessie
    resultaat_id = request.session.get(SESSION_KEY_RESULTAAT_ID)
    resultaat = None
    
    if resultaat_id:
        resultaat = Resultaat.objects.filter(id=resultaat_id).first()
    
    if resultaat is None:
        # Maak een nieuw resultaat
        resultaat = _sla_resultaat_op(
            request,
            gemeente_zoekterm,
            gevonden_gemeente,
            vragen,
            antwoorden,
            totale_score,
            max_mogelijke_score,
            risico,
        )
        request.session[SESSION_KEY_RESULTAAT_ID] = resultaat.id
        request.session.modified = True
    else:
        # Update het bestaande resultaat met de gemeente en nieuwe gegevens
        resultaat.gemeente_zoekterm = gemeente_zoekterm
        resultaat.gemeente = gevonden_gemeente
        resultaat.save()
        # Verwijder oude antwoorden en maak nieuwe aan
        Antwoord.objects.filter(resultaat=resultaat).delete()
        for vraag in vragen:
            ja_antwoord = bool(antwoorden.get(str(vraag.id), False))
            Antwoord.objects.create(
                resultaat=resultaat,
                vraag=vraag,
                ja_nee=ja_antwoord,
                behaalde_score=vraag.weging if ja_antwoord else vraag.weging_nee,
            )

    resultaat_antwoorden = list(
        resultaat.antwoorden.select_related('vraag').order_by('vraag__volgorde', 'vraag__id')
    )
    antwoorden = {str(antwoord.vraag_id): bool(antwoord.ja_nee) for antwoord in resultaat_antwoorden}
    
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
        'max_score': max_mogelijke_score,
        'risico': risico,
        'feedback': feedback_dict[risico],
        'categoriescore': categoriescore,
        'antwoorden': antwoorden,
        'vragen': vragen,
        'resultaat': resultaat,
        'resultaat_antwoorden': resultaat_antwoorden,
        'gemeente_zoekterm': gemeente_zoekterm,
        'gevonden_gemeente': gevonden_gemeente,
        'gemeente_meldingen': gemeente_meldingen,
    }
    
    return render(request, 'resultaten/resultaten.html', context)


def pdf_download(request):
    if not request.session.get(SESSION_KEY_VOLTOOID, False):
        return redirect('/vragen/')

    if not request.session.session_key:
        request.session.save()

    gemeente_zoekterm = (request.POST.get('gemeente_zoekterm') or request.GET.get('gemeente') or '').strip()
    gevonden_gemeente, _ = _zoek_gemeente(gemeente_zoekterm)

    resultaat_id = request.session.get(SESSION_KEY_RESULTAAT_ID)
    resultaat = None
    if resultaat_id:
        resultaat = Resultaat.objects.filter(id=resultaat_id).first()
    if resultaat is None:
        resultaat = (
            Resultaat.objects.filter(sessie_key=request.session.session_key or '')
            .order_by('-aangemaakt_op')
            .first()
        )

    if resultaat is None:
        return HttpResponse('No saved result available', status=400)

    resultaat_antwoorden = list(
        resultaat.antwoorden.select_related('vraag').order_by('vraag__volgorde', 'vraag__id')
    )
    db_antwoorden = {str(antwoord.vraag_id): bool(antwoord.ja_nee) for antwoord in resultaat_antwoorden}
    resultaat_vragen = [antwoord.vraag for antwoord in resultaat_antwoorden]
    totale_score, categoriescore, max_mogelijke_score = _bereken_score(db_antwoorden, resultaat_vragen)
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
        'resultaat': resultaat,
        'resultaat_antwoorden': resultaat_antwoorden,
        'totale_score': totale_score,
        'max_score': max_mogelijke_score,
        'risico': risico,
        'feedback': feedback_dict[risico],
        'categoriescore': categoriescore,
        'antwoorden': db_antwoorden,
        'vragen': resultaat_vragen,
    }

    return render(request, 'resultaten/pdf_template.html', context)


@require_http_methods(['POST'])
def delete_resultaat(request):
    """Verwijder het resultaat van de huidige sessie."""
    if not request.session.get(SESSION_KEY_VOLTOOID, False):
        return JsonResponse({'success': False, 'error': 'Geen actieve vragenlijst.'}, status=403)
    
    resultaat_id = request.session.get(SESSION_KEY_RESULTAAT_ID)
    if not resultaat_id:
        return JsonResponse({'success': False, 'error': 'Geen resultaat gevonden.'}, status=404)
    
    try:
        resultaat = Resultaat.objects.get(id=resultaat_id)
        resultaat.delete()
        # Verwijder ook de session key
        if SESSION_KEY_RESULTAAT_ID in request.session:
            del request.session[SESSION_KEY_RESULTAAT_ID]
            request.session.modified = True
        return JsonResponse({'success': True, 'message': 'Resultaat verwijderd.'})
    except Resultaat.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Resultaat niet gevonden.'}, status=404)
