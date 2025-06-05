from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TutorViewSet, PacienteViewSet

# Cria um router e registra viewsets com ele
router = DefaultRouter()
router.register(r'tutores', TutorViewSet, basename='tutor')
# Registra o viewset de Paciente com o router
router.register(r'pacientes', PacienteViewSet, basename='paciente')

urlpatterns = [
    path('', include(router.urls)),
]
