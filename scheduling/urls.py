from django.conf.urls import url

from scheduling.views import GaView, ProjectView, BranchAndBoundView

urlpatterns = [
    url(r'^project/(?P<project_id>\d+)/$', ProjectView.as_view(), name='project'),
    url(r'^ga/$', GaView.as_view(), name='ga'),
    url(r'^bab/$', BranchAndBoundView.as_view(), name='branch_and_bound'),
]