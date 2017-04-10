# coding=utf-8
from __future__ import unicode_literals
from django import forms

from scheduling.models import Project, ProjectMember


class AddProjectForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(AddProjectForm, self).__init__(*args, **kwargs)
        self.user = user

    class Meta:
        model = Project
        fields = ('name',)

    def save(self, commit=True):
        instance = super(AddProjectForm, self).save(commit=False)
        instance.author = self.user
        if commit:
            instance.save()
            membership = ProjectMember(user=self.user, project=instance, is_project_admin=True)
            membership.save()
        return instance


class GeneticAlgorithmForm(forms.Form):
    probability_crossover = forms.FloatField(label='Соотношение кроссинговера к мутации', min_value=0,
                                             max_value=1)
    population_size = forms.IntegerField(label='Количество особей в популяции')
    limit = forms.IntegerField(label='Максимальное число популяций')