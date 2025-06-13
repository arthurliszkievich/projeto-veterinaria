from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TutorViewSet,
    PacienteViewSet,
    VeterinarioViewSet,
    ConsultaViewSet,
    SintomaViewSet,
    DoencaViewSet,
)

# Cria um router e registra viewsets com ele
router = DefaultRouter()
router.register(r"tutores", TutorViewSet, basename="tutor")
router.register(r"pacientes", PacienteViewSet, basename="paciente")
router.register(r"veterinarios", VeterinarioViewSet, basename="veterinario")
router.register(r"consultas", ConsultaViewSet, basename="consulta")
router.register(r"sintomas", SintomaViewSet, basename="sintoma")
router.register(r'doencas', DoencaViewSet, basename='doenca')

urlpatterns = [
    path("", include(router.urls)),
]
