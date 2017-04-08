# coding=utf-8
from __future__ import unicode_literals
from django import forms
from django.core.exceptions import ValidationError

from core.models import User

NOT_THE_SAME = 'Пароль и подтверждение не совпадают'


class RegisterForm(forms.ModelForm):
    password = forms.CharField(max_length=128, label='Пароль', widget=forms.PasswordInput)
    confirm = forms.CharField(max_length=128, label='Подтверждение', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get('password')
        confirm = cleaned_data.get('confirm')
        if password != confirm:
            raise ValidationError({'confirm': NOT_THE_SAME})
        return cleaned_data

    def save(self, commit=True):
        instance = super(RegisterForm, self).save(commit=False)
        instance.email = User.objects.normalize_email(instance.email)
        instance.set_password(instance.password)
        if commit:
            instance.save()
        return instance


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=128, label='Email')
    password = forms.CharField(max_length=128, label='Пароль', widget=forms.PasswordInput)