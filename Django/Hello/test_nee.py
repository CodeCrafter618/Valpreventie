import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hello.settings')
django.setup()

from django.test import Client
from home.models import Vragen

client = Client()
vragen = list(Vragen.objects.order_by('volgorde', 'id'))
print(f'Aantal vragen: {len(vragen)}')

# Reset session
client.get('/vragen/?opnieuw=1')

for i in range(len(vragen)):
    resp = client.post(f'/vragen/?stap={i}', {'keuze': 'nee'})
    location = resp.get('Location', 'n/a')
    print(f'Vraag {i+1}/{len(vragen)}: {resp.status_code} -> {location}')

print('Klaar! Ga naar http://127.0.0.1:8000/resultaten/')
