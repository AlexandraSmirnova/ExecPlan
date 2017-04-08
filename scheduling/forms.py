# coding=utf-8
from __future__ import unicode_literals
from django import forms


class GeneticAlgorithmForm(forms.Form):
    probability_crossover = forms.FloatField(label='Соотношение кроссинговера к мутации', min_value=0,
                                             max_value=1)
    population_size = forms.IntegerField(label='Количество особей в популяции')
    limit = forms.IntegerField(label='Максимальное число популяций')