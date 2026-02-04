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
from django.views.generic import TemplateView
from django.views.static import serve
from django.urls import re_path

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
    # --- FRONTEND PAGES (Interface do Usuário) ---
    path("", TemplateView.as_view(template_name="index.html"), name="home"),
    path("login-funcionario/", TemplateView.as_view(template_name="login-funcionario.html"), name="login-funcionario"),
    path("registro-funcionario/", TemplateView.as_view(template_name="registro-funcionario.html"), name="registro-funcionario"),
    path("login-gerente/", TemplateView.as_view(template_name="login-gerente.html"), name="login-gerente"),
    path("dashboard/", TemplateView.as_view(template_name="dashboard.html"), name="dashboard"),
    path("pacientes/", TemplateView.as_view(template_name="pacientes.html"), name="pacientes"),
    path("novo-paciente/", TemplateView.as_view(template_name="novo-paciente.html"), name="novo-paciente"),
    path("novo-tutor/", TemplateView.as_view(template_name="novo-tutor.html"), name="novo-tutor"),
    path("consulta/", TemplateView.as_view(template_name="consulta.html"), name="consulta"),
    
    # --- ADMIN URL ---
    path("admin/", admin.site.urls),
    
    # --- API v1 URLS (Versionamento) ---
    path("api/v1/", include("clinic.urls")),
    # Alias sem versionamento (aponta para v1)
    path("api/", include("clinic.urls")),
    # --- TOKEN JWT URLS ---
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # --- DOCUMENTATION URLS ---
    path(
        "api/schema/", SpectacularAPIView.as_view(), name="schema"
    ),  # Gera o schema da API
    # Swagger UI:
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Redoc UI:
    path(
        "api/schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    # ---------------------------------------------------------
    # --- DRF BROWSABLE API AUTH URLS ---
    # URLs de Autenticação do Django REST Framework (para a API Navegável)
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    
    # --- FRONTEND STATIC FILES ---
    re_path(r'^(?P<path>style\.css|script\.js)$', serve, {'document_root': settings.BASE_DIR / 'frontend'}),
]

# Servir Arquivos de Mídia em Desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
