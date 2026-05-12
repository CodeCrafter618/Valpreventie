# 🏠 Valpreventie Risicotest - Handleiding

## Wat is dit project?

Dit is een webapplicatie waarmee ouderen zelf kunnen testen of hun huis veilig is voor valpreventie. Gebruikers beantwoorden vragen, en aan het einde krijgen ze een score en contactgegevens van hun gemeente voor hulp.

**Voorbeeld:** Een 75-jarige vrouw kan dit systeem gebruiken om te checken of haar badkamer veilig is en of ze misschien handgrepen nodig heeft.

---

## 📊 Hoe werkt het systeem?

```
Gebruiker logt in → Beantwoordt vragen → Krijgt score → Zoekt gemeente → Drukt resultaat af
```

1. **Inloggen** → Gebruiker voert gebruikersnaam/e-mail en wachtwoord in
2. **Vragen beantwoorden** → Stap voor stap vragen met Ja/Nee antwoorden
3. **Resultaten zien** → Gedetailleerde score per categorie
4. **Gemeente zoeken** → Opzoeken van contactgegevens
5. **Afdrukken** → Resultaten afdrukken (en verwijderen uit admin)

---

## Projectoverzicht

### Doel

Het bieden van een interactieve risicotest voor valpreventie, waarbij gebruikers vragen beantwoorden over hun thuissituatie en aan het einde een gedetailleerd rapport ontvangen met hun risicoscore en contactgegevens van hun gemeente.

### Kernfunctionaliteiten

- 👤 **Inlogfunctionaliteit** - Gebruikers kunnen inloggen met gebruikersnaam of e-mailadres
- ❓ **Interactieve vragenlijst** - Stap-voor-stap vragenlijst met voortgangsbalk
- 📊 **Resultatenweergave** - Gedetailleerde scores per categorie
- 🏢 **Gemeente informatie** - Opzoeken van contactgegevens
- 🗂️ **Vraaglijstbeheer** - Admin interface voor vraagbeheer
- ➕ **Vraag toevoegen** - Nieuwe vragen kunnen worden toegevoegd
- 🖨️ **Afdrukfunctie** - Resultaten kunnen worden afgedrukt/geëxporteerd

---

## Databasestructuur

### Models

#### 1. **Vragen**

Bevat alle valpreventievragen in de risicotest.

| Veld         | Type           | Beschrijving                               |
| ------------ | -------------- | ------------------------------------------ |
| `id`         | AutoField      | Primaire sleutel                           |
| `categorie`  | CharField(80)  | Categorienaam (bijv. "Controleer je ogen") |
| `emoji`      | CharField(16)  | Emoji voor visuele representatie           |
| `vraag`      | CharField(255) | De volledige vraagtext                     |
| `extra_info` | CharField(255) | Extra informatie/tips                      |
| `weging`     | IntegerField   | Score voor "Ja" antwoord (default: 0)      |
| `weging_nee` | IntegerField   | Score voor "Nee" antwoord (default: 0)     |
| `volgorde`   | IntegerField   | Volgordeindex in de vragenlijst            |

**Relaties:**

- `antwoorden` - Reverse relation naar Antwoord model

---

#### 2. **Gemeente**

Bevat informatie over nederlandse gemeenten voor contactgegevens.

| Veld             | Type           | Beschrijving                      |
| ---------------- | -------------- | --------------------------------- |
| `id`             | AutoField      | Primaire sleutel                  |
| `naam`           | CharField(255) | Gemeentenaam                      |
| `telefoonnummer` | CharField(255) | Contactnummer (optioneel)         |
| `adres`          | CharField(255) | Adres van de gemeente (optioneel) |

**Relaties:**

- `resultaten` - Reverse relation naar Resultaat model

---

#### 3. **Resultaat**

Slaat de uitkomsten van een voltooide risicotest op.

| Veld                | Type                  | Beschrijving                                      |
| ------------------- | --------------------- | ------------------------------------------------- |
| `id`                | AutoField             | Primaire sleutel                                  |
| `sessie_key`        | CharField(40)         | Django sessie ID                                  |
| `gemeente_zoekterm` | CharField(255)        | Gezochte gemeentenaam                             |
| `gemeente`          | ForeignKey (Gemeente) | Geselecteerde gemeente (nullable)                 |
| `totale_score`      | IntegerField          | Totale score behaald                              |
| `max_score`         | IntegerField          | Maximaal mogelijke score                          |
| `risico`            | CharField(20)         | Risicoclassificatie ("laag", "gemiddeld", "hoog") |
| `aangemaakt_op`     | DateTimeField         | Timestamp van aanmaak                             |

**Relaties:**

- `antwoorden` - Reverse relation naar Antwoord model

---

#### 4. **Antwoord**

Slaat individuele antwoorden van een resultaat op.

| Veld             | Type                   | Beschrijving                   |
| ---------------- | ---------------------- | ------------------------------ |
| `id`             | AutoField              | Primaire sleutel               |
| `resultaat`      | ForeignKey (Resultaat) | Gekoppeld resultaat (nullable) |
| `vraag`          | ForeignKey (Vragen)    | Gekoppelde vraag               |
| `ja_nee`         | BooleanField           | True = Ja, False = Nee         |
| `behaalde_score` | IntegerField           | Punten voor dit antwoord       |
| `aangemaakt_op`  | DateTimeField          | Timestamp van aanmaak          |

---

#### 5. **Question** (Legacy)

Oud model, niet actief gebruikt.

---

## Applicatiepagina's

### 1. **Homepage** (`/`)

**App:** `home`  
**View:** `home.views.index`  
**Template:** `home/index.html`

**Functionaliteit:**

- Welcomepagina van de applicatie
- Startpunt voor nieuwe gebruikers

**Context Data:**
Geen specifieke context data

**Screenshot Details:**

- Header en footer
- Navigatielinks naar andere delen van de site

---

### 2. **Inlogpagina** (`/login/`)

**App:** `login`  
**View:** `login.views.index`  
**Template:** `login/login.html`

**Functionaliteit:**

- Gebruikers kunnen inloggen met gebruikersnaam OF e-mailadres
- Validatie van gebruikersinformatie
- Error berichten voor incorrect gebruik

**Request Method:** POST

**Form Fields:**

- `username` - Gebruikersnaam of e-mailadres
- `password` - Wachtwoord

**Context Data:**

- Foutmeldingen van Django messages framework

**Validatie Regels:**

1. Gebruikersnaam/e-mail mag niet leeg zijn
2. Gebruiker moet bestaan in database
3. Gebruiker account moet actief zijn (is_active=True)
4. Wachtwoord moet correct zijn

**Response:**

- ✅ Succesvol: Redirect naar `/` met ingelogde gebruiker
- ❌ Fout: Hertoont login pagina met foutmelding

---

### 3. **Vragenlijstpagina** (`/vragen/`)

**App:** `vragen`  
**View:** `vragen.views.index`  
**Template:** `vragen/vragen.html`

**Functionaliteit:**

- Interactieve stap-voor-stap vragenlijst
- Voortgangsbalk toont huidige positie
- Volgende/Vorige navigatie
- Sessie-based antwoordopslag
- Automatische categorie-erkenning per vraag

**Query Parameters:**

- `stap` - Huidige vraagindex (0-based)
- `opnieuw` - Resetvlag (waarde: "1") om vragenlijst opnieuw te starten

**Request Method:** GET/POST

**Form Fields:**

- `keuze` - Gebruiker antwoord ("ja" of "nee")

**Validatie:**

- Gebruiker moet een keuze maken (ja/nee)
- Index moet binnen geldige vraagrange liggen

**Session Storage:**

```python
{
    'vragenlijst_voltooid': False,  # True wanneer alle vragen beantwoord
    'vragenlijst_resultaat_antwoorden': {
        'vraag_id': True/False,  # True=Ja, False=Nee
        ...
    }
}
```

**Context Data:**

- `heeft_vragen` - Boolean: zijn er vragen beschikbaar
- `totaal` - Totaal aantal vragen
- `huidige_vraag` - Huidge Vragen object
- `extra_info_intro` - Eerste regel van extra info
- `extra_info_subtitel` - Tweede regel van extra info
- `extra_info_punten` - Bulletpoints van extra info (regel 3+)
- `antwoorden` - Dict met alle antwoorden tot nu toe
- `voortgang` - Percentage van voltooiing (0-100)
- `bestaand_antwoord` - Eerder gegeven antwoord voor huiding vraag
- `gekozen_keuze` - Visueel geselecteerde keuze ("ja"/"nee"/"")
- `foutmelding` - Validation error message

**Response:**

- Volgende vraag: Redirect naar `/vragen/?stap={next_index}`
- Laatste vraag voltooid: Redirect naar `/resultaten/`
- Error: Hertoont huoding vraag met foutmelding

---

### 4. **Resultatenpagina** (`/resultaten/`)

**App:** `resultaten`  
**View:** `resultaten.views.resultaten`  
**Template:** `resultaten/resultaten.html`

**Functionaliteit:**

- Toont gedetailleerde risicoscore en feedback
- Gemeente lookup/search functionaliteit
- Categorieën met scores weergegeven als kaarten
- Afdruk/printoptie
- Resultaat kan worden verwijderd uit admin bij afdrukken

**Vereisten:**

- Gebruiker moet `vragenlijst_voltooid` in sessie hebben staan
- Vragen moeten beschikbaar zijn in database

**Query Parameters:**

- `gemeente` - Gemeente zoeknaam

**Request Method:** GET

**Database Operaties:**

1. Controleer/maak Resultaat aan voor huiding sessie
2. Update Antwoord records wanneer gemeente wordt gewijzigd
3. Resultaat kan worden verwijderd via `/resultaten/delete/` POST

**Context Data:**

- `heeft_vragen` - Boolean
- `totale_score` - Totaal behaalde punten
- `max_score` - Maximum mogelijke punten
- `risico` - Risicoclassificatie
- `feedback` - Dict met `titel`, `tekst`, `kleur`
- `categoriescore` - Dict per categorie met:
  - `score` - Behaalde score
  - `totaal` - Max score
  - `aantal_vragen` - Aantal vragen
  - `emoji` - Categorie emoji
  - `beschrijving` - Feedback tekst
  - `toon_kans_op` - Boolean
- `gemeente_zoekterm` - Ingevoerde zoeknaam
- `gevonden_gemeente` - Gemeente object of None
- `gemeente_meldingen` - Array van error/info messages

**Risicoclassificatie:**

```
percentage >= 85% → "laag" (groen)
percentage >= 60% → "gemiddeld" (oranje)
percentage < 60%  → "hoog" (rood)
```

**Afdruk Functie:**

- Knop roept JavaScript functie `deleteAndPrint()` aan
- AJAX POST naar `/resultaten/delete/` om resultaat te verwijderen
- Vervolgens `window.print()` voor browser printdialoog

---

### 5. **PDF/Print Template** (`/resultaten/pdf/`)

**App:** `resultaten`  
**View:** `resultaten.views.pdf_download`  
**Template:** `resultaten/pdf_template.html`

**Functionaliteit:**

- Print-optimized versie van resultaten
- Kan gebruikt worden voor PDF export via browser
- Toont dezelfde informatie als resultatenpagina

**Request Method:** POST/GET

**Context Data:**

- Zelfde als Resultatenpagina

**Response:**

- HTML template optimized voor printing

---

### 6. **Vraaglijstbeheer** (`/vragenlijstbeheer/`)

**App:** `vragenlijstbeheer`  
**View:** `vragenlijstbeheer.views.index`  
**Template:** `vragenlijstbeheer/index.html`

**Functionaliteit:**

- Admin interface voor het beheren van vragen
- Vragen kunnen bewerkt en verwijderd worden
- Overzicht van alle vragen in database
- Sortering op volgorde

**Request Method:** GET/POST

**Query Parameters:**

- `edit` - ID van te bewerken vraag

**Form Fields (POST):**

- `actie` - "verwijder" of "opslaan"
- `vraag_id` - ID van te bewerken/verwijderde vraag
- `vraag` - Vraagtekst
- `extra_info` - Extra info/tips
- `volgorde` - Volgordenummer
- `weging` - Score voor "Ja"
- `weging_nee` - Score voor "Nee"

**Database Operaties:**

- Verwijderen: `Vragen.delete()`
- Opslaan: `Vragen.save()`
- Automatische categorie/emoji bepaling via `bepaal_standaard_meta()`

**Context Data:**

- `vragen` - QuerySet van alle Vragen
- `edit_id` - ID van vigerende bewerkingsvraag

---

### 7. **Vraag Toevoegen** (`/vraag-toevoegen/`)

**App:** `vraag_toevoegen`  
**View:** `vraag_toevoegen.views.index`  
**Template:** `vraag_toevoegen/index.html`

**Functionaliteit:**

- Formulier om nieuwe vragen toe te voegen
- Automatische volgorde bepaling (next sequence)
- Automatische categorie en emoji bepaling

**Request Method:** GET/POST

**Form Fields (POST):**

- `vraag` - Vraagtekst (verplicht)
- `extra_info` - Extra informatie (optioneel)
- `weging` - Score voor "Ja" (optioneel, default: 0)
- `weging_nee` - Score voor "Nee" (optioneel, default: 0)
- `volgorde` - Volgordenummer (optioneel, default: volgende)

**Database Operaties:**

- Nieuwe Vragen record aanmaken
- Categorie en emoji automatisch bepaald

**Context Data:**

- `volgende_volgorde` - Aanbevolen volgordenummer

**Response:**

- ✅ Succesvol: Redirect naar `/vragenlijstbeheer/`
- ❌ Fout: Hertoont formulier

---

### 8. **Resultaat Verwijderen** (`/resultaten/delete/`)

**App:** `resultaten`  
**View:** `resultaten.views.delete_resultaat`

**Functionaliteit:**

- Verwijdert het huidage resultaat uit database
- Aangeroepen via AJAX vanuit resultaten pagina
- Gebruikt wanneer gebruiker op "Afdrukken" klikt

**Request Method:** POST

**Headers Required:**

- `X-CSRFToken` - CSRF token uit cookie

**Response Format:** JSON

```json
{
  "success": true,
  "message": "Resultaat verwijderd."
}
```

**Error Responses:**

```json
{
  "success": false,
  "error": "Geen actieve vragenlijst."
}
```

---

## URL Routes

### Hoofd URL Configuratie (`Hello/urls.py`)

```python
/                           → home.views.index
/login/                     → login.views.index
/vragen/                    → vragen.views.index
/resultaten/                → resultaten.views.resultaten
/resultaten/pdf/            → resultaten.views.pdf_download
/resultaten/delete/         → resultaten.views.delete_resultaat
/vragenlijstbeheer/         → vragenlijstbeheer.views.index
/vraag-toevoegen/           → vraag_toevoegen.views.index
/admin/                     → Django Admin Interface
```

### App-specifieke URL Configuraties

Elke app heeft een eigen `urls.py` bestand dat inbegrepen wordt in de hoofd-urls.py.

---

## Sessie Management

De applicatie gebruikt Django sessies voor:

```python
SESSION_KEY_VOLTOOID = 'vragenlijst_voltooid'                    # Boolean
SESSION_KEY_ANTWOORDEN = 'vragenlijst_resultaat_antwoorden'      # Dict
SESSION_KEY_RESULTAAT_ID = 'vragenlijst_resultaat_id'            # Integer
```

---

## Installatie en Configuratie

### Vereisten

- Python 3.8+
- Django 6.0
- SQLite (standaard)

### Installatiestappen

1. **Virtual Environment**

   ```bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

2. **Dependencies Installeren**

   ```bash
   pip install -r requirements.txt
   ```

3. **Database Migraties**

   ```bash
   python manage.py migrate
   ```

4. **Admin Gebruiker Aanmaken**

   ```bash
   python manage.py createsuperuser
   ```

5. **Gemeenten Importeren** (optioneel)

   ```bash
   python manage.py import_gemeenten
   ```

6. **Server Starten**
   ```bash
   python manage.py runserver
   ```

Bezoek http://localhost:8000 in uw browser.

---

## Admin Interface

Toegang via `/admin/` met superuser credentials.

### Beheerbare Modellen

- ✅ Gemeente
- ✅ Vragen
- ✅ Resultaat
- ✅ Antwoord

### Admin Features

- Zoeken en filteren
- Inline bewerking van antwoorden
- Read-only velden voor metadata

---

## Hulpfuncties

### categorie_herkenning.py

Automatisch bepaalt categorie en emoji op basis van vraagtext.

### result_filters.py (Template Filters)

Aangepaste Django template filters voor resultaten weergave.

---

## Security Features

- ✅ CSRF Token bescherming
- ✅ Sessie-based autenticatie
- ✅ Admin interface beveiligd
- ✅ Gebruikersinput validatie

---

## Opmerkingen voor Developers

1. **Vraagvolgorde:** Altijd volgorde+id gebruiken voor stabiele sortering
2. **Sessie Keys:** Altijd controleren of sessie bestaat voordat deze gebruikt wordt
3. **Gemeente Lookup:** Case-insensitive zoeking wordt ondersteund
4. **Scores:** Max van ja/nee weging wordt gebruikt als maximale score

---

## 💻 Hoe werkt de code?

### Inhoudsopgave Code Voorbeelden

- [Django Architecture](#django-architecture-mtv-model)
- [Models](#hoe-models-werken-database-tabellen)
- [Views](#hoe-views-werken-de-logica)
- [Sessies](#hoe-sessies-werken-geheugen-per-gebruiker)
- [Templates](#hoe-templates-werken-html--variabelen)
- [Formulieren](#hoe-formulieren-werken)
- [Database Queries](#hoe-queries-werken-database-vragen)
- [Resultatenpagina Flow](#hoe-de-resultatenpagina-werkt)
- [Delete Mechanisme](#hoe-delete-afdrukken-werkt)
- [Admin Interface](#hoe-admin-interface-werkt)
- [Authenticatie](#hoe-authenticatie-werkt-inloggen)
- [Compleet Flow Diagram](#flow-diagram---compleet-voorbeeld)

---

### Django Architecture (MTV Model)

Django volgt het **MTV patroon** (Model-Template-View):

```
Gebruiker bezoekt URL
        ↓
Django zoekt bijbehorende View
        ↓
View haalt gegevens uit Model (Database)
        ↓
View stuurt data naar Template
        ↓
Template toont HTML aan gebruiker
```

**Voorbeeld: Vragen pagina**

```
1. Gebruiker gaat naar /vragen/
   ↓
2. Django roept vragen.views.index() aan (📁 vragen/views.py)
   ↓
3. View vraagt vragen op uit database via Vragen.objects.all() (📁 home/models.py)
   ↓
4. View stuurt vraag naar template (📁 vragen/templates/vragen/vragen.html)
   ↓
5. Template toont vraag + formulier in HTML
```

---

### Hoe Models werken (Database tabellen)

**Bestand:** `home/models.py`  
**Gebruikt op pagina's:** `/vragen/`, `/resultaten/`, `/vragenlijstbeheer/`, `/admin/`  
**URL:** Alle pagina's die gegevens uit database halen

**Model = Blueprint van database tabel**

```python
# home/models.py
class Vragen(models.Model):
    vraag = models.CharField(max_length=255)
    weging = models.IntegerField(default=0)
    volgorde = models.IntegerField()

    def __str__(self):
        return self.vraag
```

Dit maakt een tabel in de database:

```
┌─────────────────────────────────────────┐
│ Vragen Tabel (db.sqlite3)               │
├─────┬──────────────┬────────┬───────────┤
│ id  │ vraag        │ weging │ volgorde  │
├─────┼──────────────┼────────┼───────────┤
│ 1   │ Ziet u goed? │ 10     │ 1         │
│ 2   │ Traptreden?  │ 8      │ 2         │
└─────┴──────────────┴────────┴───────────┘
```

**Database operaties:**

```python
# home/models.py - Queries
# Alles ophalen
vragen = Vragen.objects.all()

# Filteren
vragen = Vragen.objects.filter(weging__gt=5)  # weging > 5

# Sorteren
vragen = Vragen.objects.order_by('volgorde')

# Enkel eerste
eerste_vraag = Vragen.objects.first()

# Aantal
totaal = Vragen.objects.count()
```

---

### Hoe Views werken (De logica)

**Bestand:** `vragen/views.py`, `home/views.py`, `login/views.py`, `resultaten/views.py`  
**Gebruikt op pagina's:** `/`, `/login/`, `/vragen/`, `/resultaten/`, `/admin/`  
**URL:** Elke pagina op het systeem

Een **View** is een Python functie die:

1. Request ontvangt van gebruiker
2. Data verwerkt
3. Template teruggeeft

**Eenvoudig voorbeeld (Homepage):**

```python
# home/views.py
def index(request):
    return render(request, "home/index.html")
```

Dit betekent:

1. Gebruiker vraagt `/` aan
2. Functie `index()` wordt aangeroepen
3. Het bestand `home/templates/home/index.html` wordt gerenderd
4. HTML wordt naar browser gestuurd

**Complexer voorbeeld (Vragenlijst):**

```python
# vragen/views.py
def index(request):
    # 1. Alle vragen ophalen uit database (via home/models.py)
    vragen = Vragen.objects.order_by('volgorde')

    # 2. Bepaal huidden vraagindex uit URL (?stap=0)
    huidden_index = int(request.GET.get('stap', 0))
    huidden_vraag = vragen[huidden_index]

    # 3. Check if gebruiker formulier indiende
    if request.method == "POST":
        antwoord = request.POST.get('keuze')  # "ja" of "nee"

        # 4. Sla antwoord op in sessie
        request.session['antwoorden'] = antwoord
        request.session.modified = True

        # 5. Ga naar volgende vraag
        volgende = huidden_index + 1
        return redirect(f'/vragen/?stap={volgende}')

    # 6. Stuur huidden vraag naar template (vragen/templates/vragen/vragen.html)
    return render(request, 'vragen/vragen.html', {
        'vraag': huidden_vraag,
        'totaal': len(vragen)
    })
```

**Stap voor stap:**

```
GET /vragen/?stap=0
    ↓
index() wordt aangeroepen (📁 vragen/views.py)
    ↓
vragen = [vraag1, vraag2, vraag3...]  (uit 📁 home/models.py)
    ↓
huidden_index = 0
huidden_vraag = vraag1
    ↓
return HTML template met vraag1 (📁 vragen/templates/vragen/vragen.html)
    ↓
Gebruiker ziet "Ziet u goed?"

Gebruiker klikt "Ja"
    ↓
POST request naar /vragen/
    ↓
request.POST.get('keuze') = "ja"
    ↓
request.session['antwoorden'] = "ja"
    ↓
redirect('/vragen/?stap=1')
    ↓
index() wordt weer aangeroepen met stap=1 (📁 vragen/views.py)
    ↓
Gebruiker ziet vraag 2
```

---

### Hoe Sessies werken (Geheugen per gebruiker)

**Bestand:** `vragen/views.py`, `resultaten/views.py`  
**Gebruikt op pagina's:** `/vragen/`, `/resultaten/`  
**URL:** Alle pagina's na login tot en met afdrukken

**Sessie = Tijdelijk geheugen** voor elke gebruiker

```python
# vragen/views.py en resultaten/views.py - Sessie operaties
# Opslaan in sessie
request.session['mijn_waarde'] = "hallo"
request.session.modified = True  # Sla op

# Lezen van sessie
waarde = request.session.get('mijn_waarde')  # "hallo"

# Verwijderen
del request.session['mijn_key']

# Hele sessie wissen
request.session.flush()
```

**In ons project:**

```python
# vragen/views.py - Antwoorden opslaan
request.session['vragenlijst_antwoorden'] = {
    '1': True,      # Vraag 1: Ja
    '2': False,     # Vraag 2: Nee
    '3': True       # Vraag 3: Ja
}

# resultaten/views.py - Markeer als voltooid
request.session['vragenlijst_voltooid'] = True

# Check of gebruiker klaar is
if request.session.get('vragenlijst_voltooid'):
    print("Gebruiker heeft alles beantwoord!")
```

**Achter de schermen:**

```
Database (db.sqlite3)
┌──────────────────────────────────────────┐
│ django_session Tabel                     │
├──────────┬──────────────┬────────────────┤
│ session  │ session_data │ expire_date    │
│ _key     │              │                │
├──────────┼──────────────┼────────────────┤
│ abc123   │ {antwoorden} │ 2026-05-15     │
└──────────┴──────────────┴────────────────┘
```

---

### Hoe Templates werken (HTML + variabelen)

**Bestand:** `vragen/templates/vragen/vragen.html`, `resultaten/templates/resultaten/resultaten.html`, `login/templates/login/login.html`  
**Gebruikt op pagina's:** `/vragen/`, `/resultaten/`, `/login/`  
**URL:** Alle pagina's met formulieren en dynamische content

Templates zijn HTML met variabelen van Python code.

**Voorbeeld template:**

```html
<!-- vragen/templates/vragen/vragen.html -->
<h1>Vraag {{ huidden_index }} van {{ totaal }}</h1>

<p>{{ vraag.vraag }}</p>

<form method="POST">
  <button name="keuze" value="ja">Ja</button>
  <button name="keuze" value="nee">Nee</button>
</form>
```

**Django roept dit aan:**

```python
# vragen/views.py
return render(request, 'vragen/vragen.html', {
    'vraag': Vragen.objects.get(id=5),  # Uit home/models.py
    'huidden_index': 3,
    'totaal': 20
})
```

**Output (HTML):**

```html
<h1>Vraag 3 van 20</h1>

<p>Ziet u goed?</p>

<form method="POST">
  <button name="keuze" value="ja">Ja</button>
  <button name="keuze" value="nee">Nee</button>
</form>
```

**Loops in templates:**

```html
<!-- Alle vragen tonen -->
<ul>
  {% for vraag in vragen %}
  <li>{{ vraag.vraag }} ({{ vraag.weging }} punten)</li>
  {% endfor %}
</ul>
```

**If statements:**

```html
<!-- resultaten/templates/resultaten/resultaten.html -->
{% if risico == "hoog" %}
<p style="color: red;">⚠️ Let op! U loopt risico!</p>
{% elif risico == "gemiddeld" %}
<p style="color: orange;">⚠️ Er zijn verbeterpunten.</p>
{% else %}
<p style="color: green;">✅ Goed bezig!</p>
{% endif %}
```

---

### Hoe Formulieren werken

**Bestand:** `vragen/templates/vragen/vragen.html`, `login/templates/login/login.html`, `vraag_toevoegen/templates/vraag_toevoegen/index.html`  
**Gebruikt op pagina's:** `/vragen/`, `/login/`, `/vraag-toevoegen/`  
**URL:** Pagina's waar gebruiker invoer geeft

**HTML formulier:**

```html
<!-- vragen/templates/vragen/vragen.html -->
<form method="POST" action="/vragen/">
  <label> <input type="radio" name="keuze" value="ja" /> Ja </label>
  <label> <input type="radio" name="keuze" value="nee" /> Nee </label>
  <button type="submit">Volgende</button>
</form>
```

**Python verwerkt het:**

```python
# vragen/views.py
if request.method == "POST":
    keuze = request.POST.get('keuze')  # "ja" of "nee"

    if keuze not in ('ja', 'nee'):
        error = "Ongeldige keuze!"
    else:
        # Opslaan...
        pass
```

**Flow:**

```
1. Gebruiker ziet formulier (📁 vragen/templates/vragen/vragen.html)
2. Klikt op "Ja" of "Nee"
3. Klikt "Volgende"
4. Browser stuurt POST request naar server
5. vragen/views.py → request.method == "POST"
6. request.POST.get('keuze') = gebruiker's keuze
7. Code verwerkt antwoord
8. Redirect naar volgende vraag
```

---

### Hoe Queries werken (Database vragen)

**Bestand:** `home/models.py` (Models) + `vragen/views.py`, `resultaten/views.py` (Queries)  
**Gebruikt op pagina's:** `/vragen/`, `/resultaten/`, `/vragenlijstbeheer/`  
**URL:** Elke pagina die data ophaalt

**Query = Vraag aan database**

```python
# resultaten/views.py - Database queries
# SELECT * FROM vragen;
vragen = Vragen.objects.all()

# SELECT * FROM vragen ORDER BY volgorde;
vragen = Vragen.objects.all().order_by('volgorde')

# SELECT * FROM vragen WHERE weging > 5;
vragen = Vragen.objects.filter(weging__gt=5)

# SELECT * FROM vragen WHERE categorie = "Oogzorg";
vragen = Vragen.objects.filter(categorie="Oogzicht")

# SELECT * FROM vragen LIMIT 1;
eerste = Vragen.objects.first()

# SELECT COUNT(*) FROM vragen;
totaal = Vragen.objects.count()

# SELECT AVG(weging) FROM vragen;
gemiddelde = Vragen.objects.aggregate(Avg('weging'))
```

**Met relaties (ForeignKey):**

```python
# resultaten/views.py - Met relaties
# Alle antwoorden van resultaat 42
antwoorden = Antwoord.objects.filter(resultaat_id=42)

# Loop door antwoorden en toon vraag
for antwoord in antwoorden:
    print(antwoord.vraag.vraag)  # Vraagtext (uit home/models.py)
    print(antwoord.ja_nee)        # True/False
    print(antwoord.behaalde_score) # Punten
```

---

### Hoe de Resultatenpagina werkt

**Bestand:** `resultaten/views.py` + `resultaten/templates/resultaten/resultaten.html`  
**Gebruikt op pagina's:** `/resultaten/`  
**URL:** Na het beantwoorden van alle vragen

**Stap 1: Check of gebruiker klaar is**

```python
# resultaten/views.py
if not request.session.get('vragenlijst_voltooid'):
    return redirect('/vragen/')
```

**Stap 2: Haal antwoorden uit sessie**

```python
# resultaten/views.py
antwoorden = request.session.get('vragenlijst_antwoorden', {})
# Voorbeeld: {'1': True, '2': False, '3': True}
```

**Stap 3: Bereken scores per categorie**

```python
# resultaten/views.py
for vraag in Vragen.objects.all():  # Uit home/models.py
    if str(vraag.id) in antwoorden:
        if antwoorden[str(vraag.id)]:  # Ja
            score += vraag.weging
        else:  # Nee
            score += vraag.weging_nee
```

**Stap 4: Bepaal risico**

```python
# resultaten/views.py
percentage = (totale_score / max_score) * 100

if percentage >= 85:
    risico = "laag"  # Groen
elif percentage >= 60:
    risico = "gemiddeld"  # Oranje
else:
    risico = "hoog"  # Rood
```

**Stap 5: Sla resultaat op in database**

```python
# resultaten/views.py
resultaat = Resultaat.objects.create(  # home/models.py
    totale_score=65,
    max_score=100,
    risico="gemiddeld"
)

# Sla alle antwoorden op
for vraag in vragen:
    Antwoord.objects.create(  # home/models.py
        resultaat=resultaat,
        vraag=vraag,
        ja_nee=antwoorden.get(str(vraag.id)),
        behaalde_score=...
    )
```

**Stap 6: Stuur data naar template**

```python
# resultaten/views.py
return render(request, 'resultaten/resultaten.html', {
    'totale_score': 65,
    'max_score': 100,
    'risico': 'gemiddeld',
    'categoriescore': {...}
})
```

---

### Hoe DELETE (Afdrukken) werkt

**Bestand:** `resultaten/templates/resultaten/resultaten.html` (JavaScript) + `resultaten/views.py` (Backend)  
**Gebruikt op pagina's:** `/resultaten/`  
**URL:** Afdruk/delete knop op resultatenpagina

**Wanneer gebruiker op "Afdrukken" klikt:**

```javascript
// resultaten/templates/resultaten/resultaten.html
function deleteAndPrint() {
  // 1. Stuur AJAX POST request
  fetch("/resultaten/delete/", {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // 3. Print pagina
        window.print();
      }
    });
}
```

**Python backend verwerkt DELETE:**

```python
# resultaten/views.py
@require_http_methods(['POST'])
def delete_resultaat(request):
    # 1. Haal resultaat ID uit sessie
    resultaat_id = request.session.get('vragenlijst_resultaat_id')

    # 2. Vind resultaat in database (home/models.py)
    resultaat = Resultaat.objects.get(id=resultaat_id)

    # 3. Verwijder uit database
    resultaat.delete()

    # 4. Verwijder sessie key
    del request.session['vragenlijst_resultaat_id']

    # 5. Stuur succes terug als JSON
    return JsonResponse({'success': True})
```

**Achter de schermen:**

```
1. Browser: "Delete resultaat 42!"
2. resultaten/views.py: "Ok, verwijdert het..."
3. Database (db.sqlite3): DELETE FROM resultaat WHERE id = 42
4. Server: "Klaar! ✅"
5. Browser: "Print pagina!"
6. Printer: "Pfffffff..." (printgeluid)
```

---

### Hoe Admin Interface werkt

**Bestand:** `home/admin.py`  
**Gebruikt op pagina's:** `/admin/`  
**URL:** Admin dashboard voor beheerders

**Django Admin geregistreerde models:**

```python
# home/admin.py
@admin.register(Resultaat)
class ResultaatAdmin(admin.ModelAdmin):
    list_display = ('id', 'risico', 'totale_score', 'aangemaakt_op')
    search_fields = ('gemeente_zoekterm',)
    list_filter = ('risico', 'aangemaakt_op')
```

**Dit maakt automatisch:**

- Tabel weergave van alle resultaten
- Zoek functie
- Filter knoppen
- Edit/Delete knoppen

**Toegang:** `/admin/` (na login met superuser)

---

### Hoe Authenticatie werkt (Inloggen)

**Bestand:** `login/views.py` + `login/templates/login/login.html`  
**Gebruikt op pagina's:** `/login/`  
**URL:** Inlogpagina, toegang tot beschermde pagina's

**Gebruiker voert wachtwoord in:**

```python
# login/views.py
def index(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 1. Zoek gebruiker (Django User model)
        user = User.objects.filter(username__iexact=username).first()

        # 2. Check wachtwoord (veilig!)
        if user and user.check_password(password):
            # 3. Activeer sessie
            auth_login(request, user)
            return redirect('/')
        else:
            # 4. Fout!
            messages.error(request, "Onjuist wachtwoord")
```

**Wat Django doet:**

```
1. Wachtwoord NIET opgeslagen als tekstbestand!
2. Django gebruikt hashing (versleuteling)
3. Bij login: control tegen gehashed versie
4. Zelfs admin ziet wachtwoord niet!
```

---

### Flow Diagram - Compleet Voorbeeld

```
┌─ GEBRUIKER BEZOEKT WEBSITE ──────────────────────────────────────┐
│                                                                    │
│  1. Browser: "GET /vragen/?stap=0"                                │
│     ↓                                                               │
│  2. Django URL Router (Hello/urls.py) zoekt route: /vragen/       │
│     ↓                                                               │
│  3. urls.py zegt: "Dit gaat naar vragen.views.index()"            │
│     ↓                                                               │
│  4. vragen/views.py → index(request) wordt aangeroepen            │
│     ↓                                                               │
│  5. Code: vragen = Vragen.objects.order_by('volgorde')            │
│     Database (db.sqlite3): "Geef me alle vragen"                  │
│     Database: "Hier zijn 20 vragen!"                              │
│     ↓                                                               │
│  6. Code: huidden_vraag = vragen[0]  # Eerste vraag               │
│     ↓                                                               │
│  7. Code: return render(request, 'vragen/vragen.html', {...})     │
│     Django: "Converteer template naar HTML"                       │
│     ↓                                                               │
│  8. Browser ontvangt HTML                                         │
│     Gebruiker ziet: "Ziet u goed?" met knoppen [Ja] [Nee]       │
│                                                                    │
│  GEBRUIKER KLIKT JA                                               │
│  ↓                                                                 │
│  9. Browser stuurt: POST /vragen/ met data: keuze=ja              │
│     ↓                                                               │
│ 10. vragen/views.py → index() weer aangeroepen (POST)             │
│     Code: if request.method == "POST":                            │
│     Code: keuze = request.POST.get('keuze')  # "ja"              │
│     ↓                                                               │
│ 11. Code: request.session['antwoorden']['1'] = True              │
│     Session opgeslagen in database                                │
│     ↓                                                               │
│ 12. Code: return redirect('/vragen/?stap=1')                      │
│     Browser: "Ga naar volgende pagina"                            │
│     ↓                                                               │
│ 13. Gebruiker ziet vraag 2: "Traptreden veilig?"                  │
│     [Proces herhaalt voor alle 20 vragen]                         │
│                                                                    │
│  NA VRAAG 20                                                      │
│  ↓                                                                 │
│ 14. vragen/views.py: request.session['vragenlijst_voltooid']=True │
│     Code: return redirect('/resultaten/')                         │
│     ↓                                                               │
│ 15. resultaten/views.py → resultaten() aangeroepen                │
│     ↓                                                               │
│ 16. Code: totale_score = berekenen(antwoorden)  # 65              │
│     Code: risico = bepaal_feedback()  # "gemiddeld"               │
│     ↓                                                               │
│ 17. Code: resultaat = Resultaat.objects.create(...)               │
│     Database (db.sqlite3): INSERT INTO resultaat...               │
│     ↓                                                               │
│ 18. Code: return render('resultaten/resultaten.html', {...})      │
│     Gebruiker ziet: Score, risico, tips                           │
│                                                                    │
│  GEBRUIKER KLIKT AFDRUKKEN                                        │
│  ↓                                                                 │
│ 19. resultaten/templates → JavaScript: fetch('/resultaten/delete/') │
│     Server (resultaten/views.py): "Verwijder dit resultaat"      │
│     Database: DELETE FROM resultaat WHERE id = 42                 │
│     ↓                                                               │
│ 20. resultaten/views.py: return JsonResponse({'success': True})   │
│     JavaScript: window.print()                                    │
│     Browser print dialog opent                                    │
│                                                                    │
│ KLAAR! ✅                                                         │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🎓 Leermomentens voor Programmeurs

**Dit project laat zien:**

1. **Model-View-Template Patroon** - Hoe code georganiseerd wordt
2. **Database Design** - ForeignKey relaties, tabellen
3. **Sessie Management** - Geheugen per gebruiker
4. **Server-side Processing** - Berekeningen op server
5. **Form Handling** - GET/POST requests
6. **AJAX** - Achtergrondverzoeken zonder pagina reload
7. **Template Language** - Dynamische HTML
8. **Security** - CSRF tokens, password hashing
9. **QuerySets** - Efficiente database queries
10. **Status Codes** - Redirects, error handling

---

_Documentatie gegenereerd: Mei 12, 2026_

---

### Hoe Models werken (Database tabellen)

**Model = Blueprint van database tabel**

```python
# home/models.py
class Vragen(models.Model):
    vraag = models.CharField(max_length=255)
    weging = models.IntegerField(default=0)
    volgorde = models.IntegerField()

    def __str__(self):
        return self.vraag
```

Dit maakt een tabel in de database:

```
┌─────────────────────────────────────────┐
│ Vragen Tabel                            │
├─────┬──────────────┬────────┬───────────┤
│ id  │ vraag        │ weging │ volgorde  │
├─────┼──────────────┼────────┼───────────┤
│ 1   │ Ziet u goed? │ 10     │ 1         │
│ 2   │ Traptreden?  │ 8      │ 2         │
└─────┴──────────────┴────────┴───────────┘
```

**Database operaties:**

```python
# Alles ophalen
vragen = Vragen.objects.all()

# Filteren
vragen = Vragen.objects.filter(weging__gt=5)  # weging > 5

# Sorteren
vragen = Vragen.objects.order_by('volgorde')

# Enkel eerste
eerste_vraag = Vragen.objects.first()

# Aantal
totaal = Vragen.objects.count()
```

---

### Hoe Views werken (De logica)

Een **View** is een Python functie die:

1. Request ontvangt van gebruiker
2. Data verwerkt
3. Template teruggeeft

**Eenvoudig voorbeeld:**

```python
# home/views.py
def index(request):
    return render(request, "home/index.html")
```

Dit betekent:

1. Gebruiker vraagt pagina aan
2. Functie `index()` wordt aangeroepen
3. Het bestand `home/index.html` wordt gerenderd (omgezet naar HTML)
4. HTML wordt naar browser gestuurd

**Complexer voorbeeld (vragenlijst):**

```python
def index(request):
    # 1. Alle vragen ophalen uit database
    vragen = Vragen.objects.order_by('volgorde')

    # 2. Bepaal huidden vraagindex uit URL
    huidden_index = int(request.GET.get('stap', 0))
    huidden_vraag = vragen[huidden_index]

    # 3. Check if gebruiker formulier indiende
    if request.method == "POST":
        antwoord = request.POST.get('keuze')  # "ja" of "nee"

        # 4. Sla antwoord op in sessie
        request.session['antwoorden'] = antwoord

        # 5. Ga naar volgende vraag
        volgende = huidden_index + 1
        return redirect(f'/vragen/?stap={volgende}')

    # 6. Stuur huidden vraag naar template
    return render(request, 'vragen/vragen.html', {
        'vraag': huidden_vraag,
        'totaal': len(vragen)
    })
```

**Stap voor stap:**

```
GET /vragen/?stap=0
    ↓
index() wordt aangeroepen
    ↓
vragen = [vraag1, vraag2, vraag3...]
    ↓
huidden_index = 0
huidden_vraag = vraag1
    ↓
return HTML template met vraag1
    ↓
Gebruiker ziet "Ziet u goed?"

Gebruiker klikt "Ja"
    ↓
POST request naar /vragen/
    ↓
request.POST.get('keuze') = "ja"
    ↓
request.session['antwoorden'] = "ja"
    ↓
redirect('/vragen/?stap=1')
    ↓
index() wordt weer aangeroepen met stap=1
    ↓
Gebruiker ziet vraag 2
```

---

### Hoe Sessies werken (Geheugen per gebruiker)

**Sessie = Tijdelijk geheugen** voor elke gebruiker

```python
# Opslaan in sessie
request.session['mijn_waarde'] = "hallo"
request.session.modified = True  # Sla op

# Lezen van sessie
waarde = request.session.get('mijn_waarde')  # "hallo"

# Verwijderen
del request.session['mijn_key']

# Hele sessie wissen
request.session.flush()
```

**In ons project:**

```python
# Sla antwoord op
request.session['vragenlijst_antwoorden'] = {
    '1': True,      # Vraag 1: Ja
    '2': False,     # Vraag 2: Nee
    '3': True       # Vraag 3: Ja
}

# Markeer als voltooid
request.session['vragenlijst_voltooid'] = True

# Check later
if request.session.get('vragenlijst_voltooid'):
    print("Gebruiker heeft alles beantwoord!")
```

**Achter de schermen:**

```
Database (db.sqlite3)
┌──────────────────────────────────────────┐
│ django_session Tabel                     │
├──────────┬──────────────┬────────────────┤
│ session  │ session_data │ expire_date    │
│ _key     │              │                │
├──────────┼──────────────┼────────────────┤
│ abc123   │ {antwoorden} │ 2026-05-15     │
└──────────┴──────────────┴────────────────┘
```

---

### Hoe Templates werken (HTML + variabelen)

Templates zijn HTML met variabelen van Python code.

**Voorbeeld template:**

```html
<!-- vragen/vragen.html -->
<h1>Vraag {{ huidden_index }} van {{ totaal }}</h1>

<p>{{ vraag.vraag }}</p>

<form method="POST">
  <button name="keuze" value="ja">Ja</button>
  <button name="keuze" value="nee">Nee</button>
</form>
```

**Django roept dit aan:**

```python
return render(request, 'vragen/vragen.html', {
    'vraag': Vragen.objects.get(id=5),
    'huidden_index': 3,
    'totaal': 20
})
```

**Output (HTML):**

```html
<h1>Vraag 3 van 20</h1>

<p>Ziet u goed?</p>

<form method="POST">
  <button name="keuze" value="ja">Ja</button>
  <button name="keuze" value="nee">Nee</button>
</form>
```

**Loops in templates:**

```html
<!-- Alle vragen tonen -->
<ul>
  {% for vraag in vragen %}
  <li>{{ vraag.vraag }} ({{ vraag.weging }} punten)</li>
  {% endfor %}
</ul>
```

**If statements:**

```html
<!-- Toon bericht als risico hoog is -->
{% if risico == "hoog" %}
<p style="color: red;">⚠️ Let op! U loopt risico!</p>
{% elif risico == "gemiddeld" %}
<p style="color: orange;">⚠️ Er zijn verbeterpunten.</p>
{% else %}
<p style="color: green;">✅ Goed bezig!</p>
{% endif %}
```

---

### Hoe Formulieren werken

**HTML formulier:**

```html
<form method="POST" action="/vragen/">
  <label> <input type="radio" name="keuze" value="ja" /> Ja </label>
  <label> <input type="radio" name="keuze" value="nee" /> Nee </label>
  <button type="submit">Volgende</button>
</form>
```

**Python verwerkt het:**

```python
if request.method == "POST":
    keuze = request.POST.get('keuze')  # "ja" of "nee"

    if keuze not in ('ja', 'nee'):
        error = "Ongeldige keuze!"
    else:
        # Opslaan...
        pass
```

**Flow:**

```
1. Gebruiker ziet formulier
2. Klikt op "Ja" of "Nee"
3. Klikt "Volgende"
4. Browser stuurt POST request naar server
5. request.method == "POST"
6. request.POST.get('keuze') = gebruiker's keuze
7. Code verwerkt antwoord
8. Redirect naar volgende vraag
```

---

### Hoe Queries werken (Database vragen)

**Query = Vraag aan database**

```python
# SELECT * FROM vragen;
vragen = Vragen.objects.all()

# SELECT * FROM vragen ORDER BY volgorde;
vragen = Vragen.objects.all().order_by('volgorde')

# SELECT * FROM vragen WHERE weging > 5;
vragen = Vragen.objects.filter(weging__gt=5)

# SELECT * FROM vragen WHERE categorie = "Oogzorg";
vragen = Vragen.objects.filter(categorie="Oogzicht")

# SELECT * FROM vragen LIMIT 1;
eerste = Vragen.objects.first()

# SELECT COUNT(*) FROM vragen;
totaal = Vragen.objects.count()

# SELECT AVG(weging) FROM vragen;
gemiddelde = Vragen.objects.aggregate(Avg('weging'))
```

**Met relaties (ForeignKey):**

```python
# Alle antwoorden van resultaat 42
antwoorden = Antwoord.objects.filter(resultaat_id=42)

# Loop door antwoorden en toon vraag
for antwoord in antwoorden:
    print(antwoord.vraag.vraag)  # Vraagtext
    print(antwoord.ja_nee)        # True/False
    print(antwoord.behaalde_score) # Punten
```

---

### Hoe de Resultatenpagina werkt

**Stap 1: Check of gebruiker klaar is**

```python
if not request.session.get('vragenlijst_voltooid'):
    return redirect('/vragen/')
```

**Stap 2: Haal antwoorden uit sessie**

```python
antwoorden = request.session.get('vragenlijst_antwoorden', {})
# Voorbeeld: {'1': True, '2': False, '3': True}
```

**Stap 3: Bereken scores per categorie**

```python
for vraag in Vragen.objects.all():
    if str(vraag.id) in antwoorden:
        if antwoorden[str(vraag.id)]:  # Ja
            score += vraag.weging
        else:  # Nee
            score += vraag.weging_nee
```

**Stap 4: Bepaal risico**

```python
percentage = (totale_score / max_score) * 100

if percentage >= 85:
    risico = "laag"  # Groen
elif percentage >= 60:
    risico = "gemiddeld"  # Oranje
else:
    risico = "hoog"  # Rood
```

**Stap 5: Sla resultaat op in database**

```python
resultaat = Resultaat.objects.create(
    totale_score=65,
    max_score=100,
    risico="gemiddeld"
)

# Sla alle antwoorden op
for vraag in vragen:
    Antwoord.objects.create(
        resultaat=resultaat,
        vraag=vraag,
        ja_nee=antwoorden.get(str(vraag.id)),
        behaalde_score=...
    )
```

**Stap 6: Stuur data naar template**

```python
return render(request, 'resultaten/resultaten.html', {
    'totale_score': 65,
    'max_score': 100,
    'risico': 'gemiddeld',
    'categoriescore': {...}
})
```

---

### Hoe DELETE (Afdrukken) werkt

**Wanneer gebruiker op "Afdrukken" klikt:**

```javascript
// resultaten.html - JavaScript
function deleteAndPrint() {
  // 1. Stuur AJAX POST request
  fetch("/resultaten/delete/", {
    method: "POST",
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // 3. Print pagina
        window.print();
      }
    });
}
```

**Python backend verwerkt DELETE:**

```python
# resultaten/views.py
@require_http_methods(['POST'])
def delete_resultaat(request):
    # 1. Haal resultaat ID uit sessie
    resultaat_id = request.session.get('vragenlijst_resultaat_id')

    # 2. Vind resultaat in database
    resultaat = Resultaat.objects.get(id=resultaat_id)

    # 3. Verwijder uit database
    resultaat.delete()

    # 4. Verwijder sessie key
    del request.session['vragenlijst_resultaat_id']

    # 5. Stuur succes terug als JSON
    return JsonResponse({'success': True})
```

**Achter de schermen:**

```
1. Browser: "Delete resultaat 42!"
2. Server: "Ok, verwijdert het..."
3. Database: DELETE FROM resultaat WHERE id = 42
4. Server: "Klaar! ✅"
5. Browser: "Print pagina!"
6. Printer: "Pfffffff..." (printgeluid)
```

---

### Hoe Admin Interface werkt

**Django Admin geregistreerde models:**

```python
# home/admin.py
@admin.register(Resultaat)
class ResultaatAdmin(admin.ModelAdmin):
    list_display = ('id', 'risico', 'totale_score', 'aangemaakt_op')
    search_fields = ('gemeente_zoekterm',)
    list_filter = ('risico', 'aangemaakt_op')
```

**Dit maakt automatisch:**

- Tabel weergave van alle resultaten
- Zoek functie
- Filter knoppen
- Edit/Delete knoppen

---

### Hoe Authenticatie werkt (Inloggen)

**Gebruiker voert wachtwoord in:**

```python
def index(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # 1. Zoek gebruiker
        user = User.objects.filter(username__iexact=username).first()

        # 2. Check wachtwoord (veilig!)
        if user and user.check_password(password):
            # 3. Activeer sessie
            auth_login(request, user)
            return redirect('/')
        else:
            # 4. Fout!
            messages.error(request, "Onjuist wachtwoord")
```

**Wat Django doet:**

```
1. Wachtwoord NIET opgeslagen als tekstbestand!
2. Django gebruikt hashing (versleuteling)
3. Bij login: control tegen gehashed versie
4. Zelfs admin ziet wachtwoord niet!
```

---

### Flow Diagram - Compleet Voorbeeld

```
┌─ GEBRUIKER BEZOEKT WEBSITE ──────────────────────────────────────┐
│                                                                    │
│  1. Browser: "Hallo, ik wil naar http://localhost:8000/vragen/"  │
│     ↓                                                               │
│  2. Django URL Router zoekt route: /vragen/                       │
│     ↓                                                               │
│  3. urls.py zegt: "Dit gaat naar vragen.views.index()"            │
│     ↓                                                               │
│  4. vragen/views.py → index(request) wordt aangeroepen            │
│     ↓                                                               │
│  5. Code: vragen = Vragen.objects.order_by('volgorde')            │
│     Database: "Geef me alle vragen, gesorteerd op volgorde"       │
│     Database: "Hier zijn 20 vragen!"                              │
│     ↓                                                               │
│  6. Code: huidden_vraag = vragen[0]  # Eerste vraag               │
│     ↓                                                               │
│  7. Code: return render(request, 'vragen.html', {...})            │
│     Django: "Converteer template naar HTML"                       │
│     ↓                                                               │
│  8. Browser ontvangt HTML met vraag 1                             │
│     Gebruiker ziet: "Ziet u goed?"                                │
│     Met knoppen: [Ja] [Nee]                                       │
│                                                                    │
│  GEBRUIKER KLIKT JA                                               │
│  ↓                                                                 │
│  9. Browser stuurt: POST /vragen/ met data: keuze=ja              │
│     ↓                                                               │
│ 10. Django roept index() weer aan, maar nu met POST               │
│     Code: if request.method == "POST":                            │
│     Code: keuze = request.POST.get('keuze')  # "ja"              │
│     ↓                                                               │
│ 11. Code: request.session['antwoorden']['1'] = True              │
│     Sessie opgeslagen: {antwoorden: {'1': True}}                  │
│     ↓                                                               │
│ 12. Code: return redirect('/vragen/?stap=1')                      │
│     Browser: "Ga naar volgende pagina"                            │
│     ↓                                                               │
│ 13. Gebruiker ziet vraag 2: "Traptreden veilig?"                  │
│     [Proces herhaalt voor all 20 vragen]                          │
│                                                                    │
│  NA VRAAG 20                                                      │
│  ↓                                                                 │
│ 14. Code: request.session['vragenlijst_voltooid'] = True          │
│     Code: return redirect('/resultaten/')                         │
│     ↓                                                               │
│ 15. Django roept resultaten.views.resultaten() aan                │
│     ↓                                                               │
│ 16. Code: totale_score = berekenen(antwoorden)  # 65              │
│     Code: risico = bepaal_feedback(totale_score)  # "gemiddeld"   │
│     ↓                                                               │
│ 17. Code: resultaat = Resultaat.objects.create(...)               │
│     Database: "Sla dit resultaat op"                              │
│     ↓                                                               │
│ 18. Code: return render('resultaten.html', {...})                 │
│     Gebruiker ziet: Score, risico, tips per categorie             │
│                                                                    │
│  GEBRUIKER KLIKT AFDRUKKEN                                        │
│  ↓                                                                 │
│ 19. JavaScript: fetch('/resultaten/delete/', ...)                 │
│     Server: "Verwijder dit resultaat"                             │
│     Database: DELETE FROM resultaat WHERE id = 42                 │
│     ↓                                                               │
│ 20. Code: return JsonResponse({'success': True})                  │
│     JavaScript: window.print()                                    │
│     Browser print dialog opent                                    │
│                                                                    │
│ KLAAR! ✅                                                         │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## 🎓 Leermomentens voor Programmeurs

**Dit project laat zien:**

1. **Model-View-Template Patroon** - Hoe code georganiseerd wordt
2. **Database Design** - ForeignKey relaties, tabellen
3. **Sessie Management** - Geheugen per gebruiker
4. **Server-side Processing** - Berekeningen op server
5. **Form Handling** - GET/POST requests
6. **AJAX** - Achtergrondverzoeken zonder pagina reload
7. **Template Language** - Dynamische HTML
8. **Security** - CSRF tokens, password hashing
9. **QuerySets** - Efficiente database queries
10. **Status Codes** - Redirects, error handling

---

_Documentatie gegenereerd: Mei 12, 2026_
