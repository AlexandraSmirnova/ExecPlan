from django.conf.urls import url

from core.views import IndexView
from scheduling.views import GaView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
]