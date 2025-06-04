"""
Django settings for config project.
"""

from pathlib import Path
import os  # Importar os
from dotenv import load_dotenv  # Importar dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Carregar variáveis de ambiente do arquivo .env
load_dotenv(BASE_DIR / '.env')  # Procura o .env na raiz do projeto Django

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
# Converte a string do .env para Boolean
DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't')

# Pega ALLOWED_HOSTS do .env e divide pela vírgula, ou usa uma lista vazia se não definido
ALLOWED_HOSTS_STRING = os.getenv('ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [host.strip()
                 for host in ALLOWED_HOSTS_STRING.split(',') if host.strip()]
# Se DEBUG=True e ALLOWED_HOSTS estiver vazio, Django permite ['localhost', '127.0.0.1'] por padrão.
# Para ser explícito, você pode adicionar:
if DEBUG and not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'clinic',
    # Apps de Terceiros
    'rest_framework',
    'dotenv',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Adicionado context_processor.debug
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': os.getenv('SQL_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('SQL_DATABASE', BASE_DIR / 'db.sqlite3'),
        'USER': os.getenv('SQL_USER'),
        'PASSWORD': os.getenv('SQL_PASSWORD'),  # Será None se não definido
        'HOST': os.getenv('SQL_HOST'),  # Será None se não definido
        'PORT': os.getenv('SQL_PORT'),  # Será None se não definido
    }
}
# Garante que NAME seja um Path para SQLite se SQL_ENGINE for sqlite3 e NAME não for um path
if DATABASES['default']['ENGINE'] == 'django.db.backends.sqlite3' and not isinstance(DATABASES['default']['NAME'], Path):
    DATABASES['default']['NAME'] = BASE_DIR / DATABASES['default']['NAME']


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'pt-br'  # Mudar para português do Brasil
TIME_ZONE = 'America/Sao_Paulo'  # Mudar para fuso horário de São Paulo

USE_I18N = True
USE_L10N = True  # Adicionado para formatação localizada (datas, números)
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'

# Diretório onde o `collectstatic` irá reunir todos os arquivos estáticos para produção.
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Diretórios adicionais onde o Django procurará por arquivos estáticos.
STATICFILES_DIRS = [
    BASE_DIR / "static", ]

# Media files (arquivos enviados por usuários)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'mediafiles'


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
