from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # El /admin/ de Django NO se monta en produccion. Sergio administra desde
    # /panel/, que es suyo y solo muestra lo que necesita; el de Django es una
    # segunda puerta con permisos totales que nadie usa. Estuvo abierto con la
    # clave del superusuario escrita en este repo PUBLICO (05-10-2026).
    *([path('admin/', admin.site.urls)] if settings.DEBUG else []),
    path('', include('core.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
