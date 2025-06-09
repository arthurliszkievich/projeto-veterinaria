# clinic/urls.py

from django.urls import path, include  # 'path' e 'include' novamente
# A ferramenta poderosa do DRF para gerar URLs
from rest_framework.routers import DefaultRouter
# Seus ViewSets que contêm a lógica da API
from .views import TutorViewSet, PacienteViewSet

# PASSO A: Criar um "Roteador"
# Pense no DefaultRouter como um assistente inteligente que sabe como criar
# todas as URLs padrão necessárias para um ModelViewSet (listar, criar, detalhar, atualizar, deletar).
router = DefaultRouter()

# PASSO B: Registrar seus ViewSets no Roteador
# Para cada ViewSet, você diz ao router:
# 1. Qual prefixo de URL usar (ex: 'tutores').
# 2. Qual ViewSet usar para esse prefixo (ex: TutorViewSet).
# 3. Um 'basename' (nome base) para as rotas geradas (útil para referências internas no Django).

# Para o TutorViewSet:
# O router vai gerar URLs como:
# - /tutores/ (para GET - listar todos, POST - criar novo)
# - /tutores/{pk}/ (para GET - detalhe, PUT/PATCH - atualizar, DELETE - deletar)
#   (Lembre-se que estas serão prefixadas por 'api/clinic/' por causa do include no config/urls.py)
router.register(r'tutores', TutorViewSet, basename='tutor')

# Para o PacienteViewSet:
# O router vai gerar URLs como:
# - /pacientes/
# - /pacientes/{pk}/
router.register(r'pacientes', PacienteViewSet, basename='paciente')

# (O 'r' antes de 'tutores' ou 'pacientes' cria uma "raw string" em Python.
#  Neste contexto, não é estritamente necessário, mas é comum ao trabalhar com
#  padrões de URL que podem, em outros cenários, usar expressões regulares.)

# PASSO C: Incluir as URLs Geradas pelo Roteador na Lista de Padrões do App
# 'router.urls' é uma lista que o DefaultRouter preencheu automaticamente com todos
# os padrões de URL que ele criou com base nos ViewSets registrados.
urlpatterns = [
    # path('', ...): O primeiro argumento '' (string vazia) significa que as URLs do router
    # serão adicionadas diretamente após o prefixo que nos trouxe até aqui (que foi 'api/clinic/').
    # include(router.urls): Diz ao Django para usar as URLs geradas pelo router.
    path('', include(router.urls)),
]
