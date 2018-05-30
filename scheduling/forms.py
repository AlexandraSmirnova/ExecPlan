# coding=utf-8
from __future__ import unicode_literals
from django import forms

from core.models import User
from scheduling.models import Project, ProjectMember, Task


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


class AddTaskForm(forms.ModelForm):
    def __init__(self, user, project_id, *args, **kwargs):
        super(AddTaskForm, self).__init__(*args, **kwargs)
        self.user = user
        for key, field in self.fields.items():
            if key == 'executors':
                members = ProjectMember.objects.filter(is_active=True, project_id=project_id)
                field.queryset = User.objects.filter(id__in=[x.user_id for x in members])
            class_name = 'form-control'
            field.widget.attrs.update({'class': class_name})

    class Meta:
        model = Task
        fields = ('name', 'description', 'duration', 'project', 'executors')
        widgets = {'project': forms.HiddenInput()}

    def save(self, commit=True):
        instance = super(AddTaskForm, self).save(commit=False)
        instance.author = self.user
        if commit:
            print 'saving....'
            instance.save()
            self.save_m2m()
        return instance


class GeneticAlgorithmForm(forms.Form):
    probability_crossover = forms.FloatField(label='Соотношение кроссинговера к мутации', min_value=0,
                                             max_value=1)
    population_size = forms.IntegerField(label='Количество особей в популяции')
    limit = forms.IntegerField(label='Максимальное число популяций')