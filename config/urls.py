from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# --- SIMPLE JWT ---
from rest_framework_simplejwt.views import (  # type: ignore
    TokenObtainPairView,
    TokenRefreshView,
)
# ---------------------------------------------

# A lista principal de padrões de URL para todo o projeto
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/clinic/", include("clinic.urls")),

    # --- ADICIONE ESTAS LINHAS PARA OS ENDPOINTS DE TOKEN JWT ---
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # ---------------------------------------------------------

    # URLs de Autenticação do Django REST Framework (para a API Navegável)
    # O Simple JWT é para autenticação baseada em token para clientes programáticos (como seu JS).
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

# PADRÃO 4 (CONDICIONAL): Servir Arquivos de Mídia em Desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
