from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static

from app import settings

urlpatterns = [
    url(r'^ssadmin/', admin.site.urls),
    url(r'^', include('core.urls', namespace='core')),
    url(r'^', include('scheduling.urls', namespace='schedule')),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)