# config/urls.py

# Importações necessárias:
from django.contrib import admin  # Para as URLs do Django Admin
# 'path' define um padrão de URL, 'include' delega para outro arquivo de URLs
from django.urls import path, include
# Para acessar as configurações do projeto (como settings.DEBUG)
from django.conf import settings
# Função helper para servir arquivos de mídia em desenvolvimento
from django.conf.urls.static import static

# A lista principal de padrões de URL para todo o projeto
urlpatterns = [
    # PADRÃO 1: Django Admin
    # Se a URL começar com "admin/", o Django encaminhará a requisição para o sistema de administração.
    # Ex: http://localhost:8000/admin/ levará à tela de login do admin.
    # Ex: http://localhost:8000/admin/clinic/tutor/ levará à lista de tutores no admin.
    path('admin/', admin.site.urls),

    # PADRÃO 2: URLs da API da Clínica
    # Se a URL começar com "api/clinic/", o Django não tentará resolvê-la completamente aqui.
    # Em vez disso, ele "corta" essa parte ("api/clinic/") e passa o restante da URL
    # para ser processado por outro arquivo de URLs: 'clinic.urls' (que é o clinic/urls.py).
    # O 'include()' é a função que faz essa delegação.
    # Ex: http://localhost:8000/api/clinic/tutores/
    #     - Django encontra 'api/clinic/' aqui.
    #     - Passa 'tutores/' para 'clinic.urls'.
    path('api/clinic/', include('clinic.urls')),

    # PADRÃO 3: URLs de Autenticação do Django REST Framework
    # O DRF fornece views e templates prontos para login e logout na API Navegável.
    # 'rest_framework.urls' é um conjunto pré-definido de padrões de URL para essas funcionalidades.
    # Ao incluí-las sob o prefixo 'api-auth/', você terá URLs como:
    #   http://localhost:8000/api-auth/login/
    #   http://localhost:8000/api-auth/logout/
    # O 'namespace' é usado internamente pelo Django para evitar conflitos de nomes de URL.
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# PADRÃO 4 (CONDICIONAL): Servir Arquivos de Mídia em Desenvolvimento
# Esta parte só é adicionada à lista 'urlpatterns' se settings.DEBUG for True.
if settings.DEBUG:
    # A função 'static()' cria um padrão de URL para servir arquivos.
    # settings.MEDIA_URL: O prefixo da URL para arquivos de mídia (ex: '/media/').
    # document_root=settings.MEDIA_ROOT: O diretório no sistema de arquivos onde as mídias estão salvas.
    # Ex: Se MEDIA_URL='/media/', uma requisição para http://localhost:8000/media/foto.jpg
    #     fará o Django procurar por 'foto.jpg' no diretório definido em MEDIA_ROOT.
    # IMPORTANTE: Isso é SÓ para desenvolvimento. Em produção, um servidor web como Nginx deve servir esses arquivos.
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
