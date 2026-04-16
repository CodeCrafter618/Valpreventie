from django.db import models


class Question(models.Model):
	question_text = models.CharField(max_length=200)
	pub_date = models.DateTimeField("date published")

	def __str__(self):
		return self.question_text


class Gemeente(models.Model):
	naam = models.CharField(max_length=255)
	contact = models.CharField(max_length=255)

	def __str__(self):
		return self.naam


class Vragen(models.Model):
	vraag = models.CharField(max_length=255)
	extra_info = models.CharField(max_length=255, blank=True)
	weging = models.IntegerField()
	volgorde = models.IntegerField()

	def __str__(self):
		return self.vraag
