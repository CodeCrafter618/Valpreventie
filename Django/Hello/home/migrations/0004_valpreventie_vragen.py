from django.db import migrations, models


def seed_valpreventie_vragen(apps, schema_editor):
    Vragen = apps.get_model("home", "Vragen")

    Vragen.objects.all().delete()

    vragen = [
        {
            "volgorde": 1,
            "categorie": "Controleer je ogen",
            "emoji": "👁️",
            "vraag": "Controleer je ogen",
            "extra_info": "Heeft u in het afgelopen jaar uw ogen laten controleren door een opticien of oogarts?",
        },
        {
            "volgorde": 2,
            "categorie": "Controleer je ogen",
            "emoji": "👁️",
            "vraag": "Draag de juiste bril",
            "extra_info": "Draagt u de juiste bril (of lenzen) voor de juiste activiteit, bijvoorbeeld een aparte leesbril en een bril voor veraf?",
        },
        {
            "volgorde": 3,
            "categorie": "Maak het huis veilig",
            "emoji": "🏠",
            "vraag": "Maak het huis veilig",
            "extra_info": "Ligt uw vloer overal vrij van obstakels zoals losse kleedjes, drempels of rondslingerende snoeren?",
        },
        {
            "volgorde": 4,
            "categorie": "Maak het huis veilig",
            "emoji": "🏠",
            "vraag": "Zorg voor goede verlichting",
            "extra_info": "Is er in elke kamer, ook op de overloop en in de badkamer, voldoende verlichting zodat u alles goed ziet?",
        },
        {
            "volgorde": 5,
            "categorie": "Maak het huis veilig",
            "emoji": "🏠",
            "vraag": "Plaats stevige handgrepen",
            "extra_info": "Zijn er stevige handgrepen aanwezig in de douche en bij het toilet?",
        },
        {
            "volgorde": 6,
            "categorie": "Eet gezond",
            "emoji": "🍎",
            "vraag": "Eet gezond",
            "extra_info": "Eet u dagelijks voldoende eiwitrijke producten zoals vlees, vis, zuivel, eieren of peulvruchten om uw spieren sterk te houden?",
        },
        {
            "volgorde": 7,
            "categorie": "Eet gezond",
            "emoji": "🍎",
            "vraag": "Drink voldoende",
            "extra_info": "Drinkt u dagelijks minstens 1,5 tot 2 liter vocht, zoals water, thee of koffie, om duizeligheid te voorkomen?",
        },
        {
            "volgorde": 8,
            "categorie": "Controleer je medicijnen",
            "emoji": "💊",
            "vraag": "Controleer je medicijnen",
            "extra_info": "Heeft u uw medicijngebruik in het afgelopen jaar besproken met uw huisarts of apotheker?",
        },
        {
            "volgorde": 9,
            "categorie": "Controleer je medicijnen",
            "emoji": "💊",
            "vraag": "Let op bijwerkingen",
            "extra_info": "Heeft u geen last van bijwerkingen zoals duizeligheid of slaperigheid door uw medicijnen?",
        },
        {
            "volgorde": 10,
            "categorie": "Beweeg voldoende",
            "emoji": "🏃",
            "vraag": "Beweeg voldoende",
            "extra_info": "Doet u minstens twee keer per week oefeningen die gericht zijn op het verbeteren van uw balans en spierkracht?",
        },
        {
            "volgorde": 11,
            "categorie": "Beweeg voldoende",
            "emoji": "🏃",
            "vraag": "Beweeg dagelijks",
            "extra_info": "Beweegt u dagelijks minstens 30 minuten, bijvoorbeeld wandelen, fietsen of tuinieren?",
        },
        {
            "volgorde": 12,
            "categorie": "Beweeg voldoende",
            "emoji": "🏃",
            "vraag": "Sta op zonder handen",
            "extra_info": "Kunt u zonder uw handen te gebruiken opstaan uit een stoel?",
        },
        {
            "volgorde": 13,
            "categorie": "Draag goede schoenen",
            "emoji": "👟",
            "vraag": "Draag goede schoenen",
            "extra_info": "Hebben uw schoenen die u dagelijks draagt een stevige, platte zool met voldoende grip?",
        },
        {
            "volgorde": 14,
            "categorie": "Draag goede schoenen",
            "emoji": "👟",
            "vraag": "Draag binnenshuis dichte schoenen",
            "extra_info": "Draagt u binnenshuis altijd dichte schoenen of pantoffels met een stevige hiel, dus geen gladde sokken of slippers?",
        },
    ]

    for vraag_data in vragen:
        Vragen.objects.create(weging=0, **vraag_data)


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0003_antwoord"),
    ]

    operations = [
        migrations.AddField(
            model_name="vragen",
            name="categorie",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.AddField(
            model_name="vragen",
            name="emoji",
            field=models.CharField(blank=True, default="", max_length=16),
        ),
        migrations.RunPython(seed_valpreventie_vragen, migrations.RunPython.noop),
    ]