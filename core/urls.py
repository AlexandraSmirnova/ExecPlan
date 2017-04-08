from django.conf.urls import url

from core.views import IndexView, LoginView, RegisterView, ProfileView, LogoutView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='home'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^profile/$', ProfileView.as_view(), name='profile'),
]