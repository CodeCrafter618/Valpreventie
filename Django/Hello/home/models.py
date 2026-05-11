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
	weging = models.IntegerField()
	volgorde = models.IntegerField()

	def __str__(self):
		return self.vraag


class Antwoord(models.Model):
	vraag = models.ForeignKey(Vragen, on_delete=models.CASCADE, related_name="antwoorden")
	ja_nee = models.BooleanField()
	aangemaakt_op = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return f"{self.vraag.vraag}: {'Ja' if self.ja_nee else 'Nee'}"
