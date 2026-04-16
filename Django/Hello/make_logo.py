from PIL import Image, ImageDraw
import os

os.makedirs('login/static/login', exist_ok=True)

# Maak een afbeelding
img = Image.new('RGB', (200, 100), color='white')
draw = ImageDraw.Draw(img)

# Teken een rood logo met letter V
draw.ellipse([50, 25, 150, 75], fill='#E74C3C', outline='#C0392B', width=2)
draw.text((75, 40), 'V', fill='white')

# Sla op als PNG
img.save('login/static/login/logo.png')
print('Logo gemaakt: login/static/login/logo.png')
