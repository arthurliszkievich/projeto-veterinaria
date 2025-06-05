from django.contrib import admin
from django.urls import path, include
# Para servir arquivos de mídia em desenvolvimento
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Prefixo para as URLs da clínica
    path('api/clinic/', include('clinic.urls')),
    # Para login/logout na API navegável
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Adicionar URLs para servir arquivos de MÍDIA em modo DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
