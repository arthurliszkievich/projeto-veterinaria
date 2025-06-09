from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TutorViewSet, PacienteViewSet, VeterinarioViewSet, ConsultaViewSet

# Cria um router e registra viewsets com ele
router = DefaultRouter()
router.register(r'tutores', TutorViewSet, basename='tutor')
router.register(r'pacientes', PacienteViewSet, basename='paciente')
router.register(r'veterinarios', VeterinarioViewSet, basename='veterinario')
router.register(r'consultas', ConsultaViewSet, basename='consulta')

urlpatterns = [
    path('', include(router.urls)),
]
