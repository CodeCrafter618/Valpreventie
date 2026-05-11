from csv import DictReader
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from home.models import Gemeente


CSV_NAME = "gemeente.csv"
OFFICIELE_NAAM = "Officiële naam"
ALTERNATIEVE_NAAM = "Alternatieve naam"
ADRESSEN = "Adressen (type, toelichting, straat, huisnummer, toevoeging, postbus, postcode, plaats, regio, provincieAfkorting, land, centroideLatitude, centroideLongitude, centroideRdx, centroideRdy)"
TELEFOONNUMMERS = "Telefoonnummers "


def normalize_text(value):
	return " ".join(value.split()) if value else ""


def parse_first_phone(value):
	phone = normalize_text(value)
	if not phone:
		return ""
	return phone.split(",", 1)[0].strip()


def parse_address_block(block):
	fields = {}
	for piece in block.split(", "):
		if ": " not in piece:
			continue
		key, value = piece.split(": ", 1)
		fields[key.strip()] = value.strip()

	street = fields.get("openbareRuimte", "")
	number = fields.get("huisnummer", "")
	addition = fields.get("toevoeging", "")
	postcode = fields.get("postcode", "")
	place = fields.get("woonplaats", "")
	postbus = fields.get("postbus", "")

	street_line = " ".join(part for part in [street, number, addition] if part)
	postal_line = " ".join(part for part in [postcode, place] if part)

	parts = []
	if street_line:
		parts.append(street_line)
	elif postbus:
		parts.append(f"Postbus {postbus}")

	if postal_line:
		parts.append(postal_line)

	return ", ".join(parts)


def parse_address(value):
	address_text = normalize_text(value)
	if not address_text:
		return ""

	blocks = [block.strip() for block in address_text.split(";") if block.strip()]
	preferred_types = ("Bezoekadres", "Woo-Adres")

	for preferred_type in preferred_types:
		for block in blocks:
			if f"adresType: {preferred_type}" in block:
				parsed = parse_address_block(block)
				if parsed:
					return parsed

	first_block = blocks[0] if blocks else ""
	return parse_address_block(first_block) or first_block


def parse_name(row):
	name = normalize_text(row.get(ALTERNATIEVE_NAAM, ""))
	if name:
		return name

	official_name = normalize_text(row.get(OFFICIELE_NAAM, ""))
	if official_name.startswith("Gemeente "):
		return official_name.removeprefix("Gemeente ").strip()
	return official_name


class Command(BaseCommand):
	help = "Import all municipalities from gemeente.csv into the database."

	def add_arguments(self, parser):
		parser.add_argument(
			"--csv-path",
			dest="csv_path",
			default=Path(settings.BASE_DIR) / CSV_NAME,
			help="Path to the gemeente.csv file.",
		)

	def handle(self, *args, **options):
		csv_path = Path(options["csv_path"])
		if not csv_path.exists():
			raise CommandError(f"CSV file not found: {csv_path}")

		municipalities = []
		with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
			reader = DictReader(handle, delimiter=";")
			for row in reader:
				name = parse_name(row)
				if not name:
					continue

				municipalities.append(
					Gemeente(
						naam=name,
						telefoonnummer=parse_first_phone(row.get(TELEFOONNUMMERS, "")),
						adres=parse_address(row.get(ADRESSEN, "")),
					)
				)

		with transaction.atomic():
			Gemeente.objects.all().delete()
			Gemeente.objects.bulk_create(municipalities, batch_size=200)

		self.stdout.write(self.style.SUCCESS(f"Geïmporteerd: {len(municipalities)} gemeenten."))