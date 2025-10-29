# config/urls.py
"""
URLs principais do projeto.

Estrutura de versionamento da API:
- /api/v1/ - Versão 1 da API (atual)
- Futuras versões poderão ser adicionadas como /api/v2/, etc.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

# ---------------------------------------------
# --- DRF-SPECTACULAR (DOCUMENTAÇÃO) IMPORTS ---
from drf_spectacular.views import (  # type: ignore
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# --- SIMPLE JWT IMPORTS ---
from rest_framework_simplejwt.views import (  # type: ignore
    TokenObtainPairView,
    TokenRefreshView,
)

# ---------------------------------------------


# A lista principal de padrões de URL para todo o projeto
urlpatterns = [
    # --- ADMIN URL ---
    path("admin/", admin.site.urls),
    # --- API v1 URLS (Versionamento) ---
    path("api/v1/", include("clinic.urls")),
    # --- TOKEN JWT URLS ---
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # --- DOCUMENTATION URLS ---
    path(
        "api/v1/schema/", SpectacularAPIView.as_view(), name="schema"
    ),  # Gera o schema da API
    # Swagger UI:
    path(
        "api/v1/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Redoc UI:
    path(
        "api/v1/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    # ---------------------------------------------------------
    # --- DRF BROWSABLE API AUTH URLS ---
    # URLs de Autenticação do Django REST Framework (para a API Navegável)
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
]

# Servir Arquivos de Mídia em Desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
