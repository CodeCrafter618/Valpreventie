from django.contrib import admin
from .models import Gemeente, Question, Vragen

admin.site.register(Question)
admin.site.register(Gemeente)
admin.site.register(Vragen)
