#!/usr/bin/env python
# Script to write template file with proper formatting

template_content = r"""{% extends "base.html" %}
{% load static %}
{% load result_filters %}

{% block title %}Resultaten - Risicotest voor vallen{% endblock %}

{% block extra_head %}
<link rel="stylesheet" href="{% static 'resultaten/resultaten.css' %}">
{% endblock %}

{% block content %}
<div class="resultaten-container">
    <div class="resultaten-header">
        <h1>Uw Risicotest Resultaten</h1>
        <p class="subtitle">Valpreventie Vragenlijst</p>
    </div>

    {% if heeft_vragen %}
    <div class="resultaten-score-section">
        <div class="score-circle" style="background-color: {% if risico == 'laag' %}#28a745{% elif risico == 'gemiddeld' %}#ffc107{% else %}#dc3545{% endif %};">
            <div class="score-number">{{ totale_score }}/{{ max_score }}</div>
            <div class="score-label">Punten</div>
        </div>
        <div class="feedback-box" style="border-left: 5px solid {% if risico == 'laag' %}#28a745{% elif risico == 'gemiddeld' %}#ffc107{% else %}#dc3545{% endif %};">
            <h2>{{ feedback.titel }}</h2>
            <p>{{ feedback.tekst }}</p>
        </div>
    </div>

    <div class="categories-intro">
        <h2>Uw bevindingen per categorie</h2>
    </div>

    <div class="categories-grid">
        {% for cat_name, cat_data in categoriescore.items %}
        <div class="category-card">
            <div class="card-emoji">{{ cat_data.emoji }}</div>
            <div class="card-title">{{ cat_name }}</div>
            <div class="card-description">{{ category_descriptions|get_item:cat_name }}</div>
            <div class="card-score">{{ cat_data.score }} van {{ cat_data.totaal }} goede gewoontes</div>
        </div>
        {% endfor %}
    </div>

    <div class="actions">
        <a href="/vragen/?opnieuw=1" class="btn btn-primary">Opnieuw Doen</a>
        <button class="btn btn-secondary" onclick="window.location.href='{% url 'resultaten:pdf_download' %}'">📥 Downloaden/Afdrukken</button>
        <a href="/" class="btn btn-tertiary">Terug naar Home</a>
    </div>

    <p class="disclaimer">
        <strong>Disclaimer:</strong> Deze vragenlijst is bedoeld als algemene indicatie. Bij twijfel over uw gezondheid of mobiliteit is het altijd verstandig om contact op te nemen met uw huisarts of een fysiotherapeut.
    </p>

    {% else %}
    <p>Er zijn geen vragen beschikbaar. Vul eerst de vragenlijst in.</p>
    {% endif %}
</div>
{% endblock %}"""

with open(r'resultaten\templates\resultaten\resultaten.html', 'w', encoding='utf-8') as f:
    f.write(template_content)
    
print("OK")
