# --- Estágio de Build ---
FROM python:3.10-slim-bookworm AS builder

# Defina variáveis de ambiente para o build
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_HOME="/opt/poetry" \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.2.0 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1 \
    PATH="/opt/poetry/bin:$PATH"

# Requisitos do sistema para compilar algumas dependências Python (ex: psycopg2)
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copie o arquivo de dependências primeiro para aproveitar o cache do Docker
COPY requirements.txt .

# Instale as dependências Python
# Local onde as dependências que precisam ser compiladas
RUN pip install --no-cache-dir -r requirements.txt


# --- Estágio de Produção (Runtime) ---
FROM python:3.10-slim-bookworm AS runtime
ARG DJANGO_SECRET_KEY_ARG

# Defina variáveis de ambiente para o runtime
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV PYTHONIOENCODING=UTF-8
ENV SECRET_KEY=${DJANGO_SECRET_KEY_ARG} 

# Crie um diretório para a aplicação e um usuário não-root
RUN groupadd -r django && useradd -r -g django django \
    && mkdir -p /home/django/web/staticfiles \
    && mkdir -p /home/django/web/mediafiles \
    && chown -R django:django /home/django

WORKDIR /home/django/web

# Copie as dependências instaladas do estágio de build
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copie o código da aplicação
COPY . .

# Comando para coletar arquivos estáticos
# Deve ser executado ANTES de mudar o proprietário se o diretório de staticfiles não tiver permissão de escrita para 'django'
# Ou crie o diretório staticfiles com as permissões corretas para o usuário 'django' antes.
# Assumindo que STATIC_ROOT em settings.py aponta para /home/django/web/staticfiles
RUN python manage.py collectstatic --noinput --clear

# Mude a propriedade dos arquivos da aplicação para o usuário django (incluindo staticfiles coletados)
RUN chown -R django:django /home/django/web

# Mude para o usuário não-root
USER django

# Exponha a porta que o Gunicorn vai rodar
EXPOSE 8000

# Comando para rodar a aplicação com Gunicorn
# Ajuste o número de workers conforme necessário (geralmente 2 * num_cores + 1)
# Ajuste 'config.wsgi:application' para o caminho do seu arquivo wsgi.py
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]