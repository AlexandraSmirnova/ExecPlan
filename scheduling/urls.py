from django.conf.urls import url

from scheduling.views import GaView, ProjectView

urlpatterns = [
    url(r'^project/(?P<project_id>\d+)/$', ProjectView.as_view(), name='project'),
    url(r'^ga/$', GaView.as_view(), name='ga'),
]