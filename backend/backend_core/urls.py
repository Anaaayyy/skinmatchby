from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from wagtail.admin import urls as wagtail_admin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtail_documents_urls

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('admin/', include(wagtail_admin_urls)),
    path('documents/', include(wagtail_documents_urls)),
    path('api/', include('api.urls')),
    path('api/forum/', include('forum.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns = urlpatterns + [
    path("", include(wagtail_urls)),
]