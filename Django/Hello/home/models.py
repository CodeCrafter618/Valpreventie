from django.db import models


class Question(models.Model):
	question_text = models.CharField(max_length=200)
	pub_date = models.DateTimeField("date published")

	def __str__(self):
		return self.question_text


class Gemeente(models.Model):
	naam = models.CharField(max_length=255)
	telefoonnummer = models.CharField(max_length=255, blank=True, default="")
	adres = models.CharField(max_length=255, blank=True, default="")

	def __str__(self):
		return self.naam


class Vragen(models.Model):
	categorie = models.CharField(max_length=80, blank=True, default="")
	emoji = models.CharField(max_length=16, blank=True, default="")
	vraag = models.CharField(max_length=255)
	extra_info = models.CharField(max_length=255, blank=True)
	weging = models.IntegerField(default=0)
	weging_nee = models.IntegerField(default=0)
	volgorde = models.IntegerField()

	def __str__(self):
		return self.vraag


class Resultaat(models.Model):
	sessie_key = models.CharField(max_length=40, blank=True, default="")
	gemeente_zoekterm = models.CharField(max_length=255, blank=True, default="")
	gemeente = models.ForeignKey(Gemeente, on_delete=models.SET_NULL, null=True, blank=True, related_name="resultaten")
	totale_score = models.IntegerField(default=0)
	max_score = models.IntegerField(default=0)
	risico = models.CharField(max_length=20, blank=True, default="")
	aangemaakt_op = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		gemeente_tekst = f" - {self.gemeente_zoekterm}" if self.gemeente_zoekterm else ""
		return f"Resultaat {self.id}{gemeente_tekst} ({self.risico or 'onbekend'})"


class Antwoord(models.Model):
	resultaat = models.ForeignKey(Resultaat, on_delete=models.CASCADE, related_name="antwoorden", null=True, blank=True)
	vraag = models.ForeignKey(Vragen, on_delete=models.CASCADE, related_name="antwoorden")
	ja_nee = models.BooleanField()
	behaalde_score = models.IntegerField(default=0)
	aangemaakt_op = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		resultaat_tekst = f"Resultaat {self.resultaat_id}" if self.resultaat_id else "Los antwoord"
		return f"{resultaat_tekst} - {self.vraag.vraag}: {'Ja' if self.ja_nee else 'Nee'}"
