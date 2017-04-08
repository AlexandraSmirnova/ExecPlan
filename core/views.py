# coding=utf-8
from __future__ import unicode_literals
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView

from app import settings
from core.forms import RegisterForm, LoginForm
from core.models import User
from scheduling.models import Project
from utils.base_views import AjaxFormView


class IndexView(TemplateView):
    template_name = 'core/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data()
        context['projects'] = Project.objects.all()
        return context


class LoginView(TemplateView, AjaxFormView):
    http_method_names = ['get', 'post']
    form_class = LoginForm
    template_name = 'core/login.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('core:home'))
        return super(LoginView, self).get(request, *args, **kwargs)

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')
        user = authenticate(email=email, password=password)
        if user:
            if user.is_active:
                login(self.request, user)
                return super(LoginView, self).form_valid(form)
            else:
                error_msg = 'Ваш аккаунт не активирован'
        else:
            error_msg = 'Введены неправильные email или пароль'

        return JsonResponse({
            'status': 'ERROR',
            'errors': error_msg
        })

    def get_success_url(self):
        return reverse('core:profile')


class LogoutView(RedirectView):
    http_method_names = ['get']
    pattern_name = 'core:home'

    def get(self, request, *args, **kwargs):
        logout(request)
        return super(LogoutView, self).get(request, *args, **kwargs)


class RegisterView(TemplateView, AjaxFormView):
    http_method_names = ['get', 'post']
    form_class = RegisterForm
    template_name = 'core/register.html'

    def get(self, request, *args, **kwargs):
        if self.request.user.is_authenticated():
            return HttpResponseRedirect(reverse('core:home'))
        return super(RegisterView, self).get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('core:home')

    def form_valid(self, form):
        form.save()
        # send_activation_email.delay(new_user)
        return super(RegisterView, self).form_valid(form)

#
# class ActivateView(RedirectView):
#     http_method_names = ['get']
#     pattern_name = 'core:profile'
#
#     def get(self, request, *args, **kwargs):
#         user_id = str_to_int(request.GET.get('uid'))
#         if user_id == 0:
#             return HttpResponseBadRequest()
#
#         request_token = request.GET.get('token')
#         if not request_token:
#             return HttpResponseBadRequest()
#
#         user = get_object_or_404(User, id=user_id)
#         user_token = get_activation_token(user)
#         if request_token != user_token:
#             return HttpResponseForbidden()
#
#         if not user.is_active:
#             user.is_active = True
#             user.save()
#
#         if request.user.is_anonymous():
#             user.backend = settings.AUTH_MODEL_BACKEND
#             login(request, user)
#         return super(ActivateView, self).get(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, DetailView):
    http_method_names = ['get']
    context_object_name = 'user'
    template_name = 'core/profile.html'

    def get_object(self, queryset=None):
        return self.request.user
