import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hello.settings')
django.setup()

from home.models import Vragen

count = Vragen.objects.count()
print(f'Aantal vragen: {count}')

if count > 0:
    vragen = Vragen.objects.all().order_by('volgorde')
    for v in vragen:
        print(f'{v.volgorde}. [{v.categorie}] {v.vraag}')
