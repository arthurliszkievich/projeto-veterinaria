from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ConsultaViewSet,
    DoencaViewSet,
    PacienteViewSet,
    SintomaViewSet,
    TutorViewSet,
    VeterinarioViewSet,
    get_user_info,
    register_user,
)

# Cria um router e registra viewsets com ele
router = DefaultRouter()
router.register(r"tutores", TutorViewSet, basename="tutor")
router.register(r"pacientes", PacienteViewSet, basename="paciente")
router.register(r"veterinarios", VeterinarioViewSet, basename="veterinario")
router.register(r"consultas", ConsultaViewSet, basename="consulta")
router.register(r"sintomas", SintomaViewSet, basename="sintoma")
router.register(r"doencas", DoencaViewSet, basename="doenca")

urlpatterns = [
    path("auth/register/", register_user, name="register"),
    path("auth/user/", get_user_info, name="user-info"),
    path("", include(router.urls)),
]
