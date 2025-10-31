# Projeto Veterinário - Sistema de Suporte a Diagnóstico

## 📖 Sobre o Projeto

Este projeto é um sistema de gestão veterinária desenvolvido com **Django** e **Django REST Framework**, projetado para auxiliar no diagnóstico clínico de pequenos animais. A principal funcionalidade é um sistema inteligente, apelidado de "Akinator Veterinário", que sugere possíveis diagnósticos com base nos sintomas apresentados pelo paciente durante uma consulta.

O back-end robusto gerencia todas as entidades (tutores, pacientes, veterinários, sintomas, doenças e consultas) e expõe uma API RESTful completa. Um front-end básico está em desenvolvimento para consumir essa API e fornecer uma interface para o registro de consultas e visualização das sugestões de diagnóstico.

## ✨ Funcionalidades Principais

### Back-end

*   **API RESTful Completa:** CRUDs para todas as entidades principais:
    *   Tutores
    *   Pacientes (Animais)
    *   Veterinários
    *   Sintomas
    *   Doenças
    *   Consultas
*   **🧠 Sistema de Suporte a Diagnóstico ("Akinator"):**
    *   Ao registrar uma consulta com os sintomas apresentados por um paciente, o sistema automaticamente consulta a base de conhecimento.
    *   Calcula um **score de proporção** para cada doença, indicando a relevância da correspondência dos sintomas.
    *   Retorna uma lista de diagnósticos suspeitos ordenada por probabilidade.
*   **Autenticação Segura:** Implementação de autenticação baseada em token JWT com `djangorestframework-simplejwt`.
*   **Filtros e Paginação:** A API suporta filtros avançados e paginação para um consumo eficiente de dados.
*   **Testes Automatizados:** Suíte de testes robusta usando `pytest` (ou `unittest` padrão do Django) e `factory_boy` para garantir a qualidade e a estabilidade do código.
*   **Containerização com Docker:** A aplicação e o banco de dados (PostgreSQL) são totalmente containerizados com Docker e Docker Compose, garantindo um ambiente de desenvolvimento e produção consistente e fácil de configurar.

### Front-end (em desenvolvimento)

*   **Interface para Nova Consulta:** Um formulário simples (HTML, CSS, JS) para registrar os dados de uma nova consulta.
*   **Carregamento Dinâmico de Sintomas:** A interface consome a API de sintomas para carregar e exibir todos os sintomas cadastrados como checkboxes selecionáveis, lidando com a paginação da API.
*   **Interação com a API:** O front-end envia os dados da consulta para o back-end e exibe os diagnósticos suspeitos retornados.

## 🛠️ Tecnologias Utilizadas

*   **Back-end:**
    *   Python 3.10+
    *   Django
    *   Django REST Framework (DRF)
    *   PostgreSQL
    *   Gunicorn
*   **Autenticação:**
    *   `djangorestframework-simplejwt`
*   **Documentação da API:**
    *   `drf-spectacular` (Swagger UI / Redoc)
*   **Testes:**
    *   `factory_boy` e `Faker` para geração de dados de teste.
*   **Front-end:**
    *   HTML5
    *   CSS3
    *   JavaScript (ES6+, com `async/await` e `fetch`)
*   **DevOps:**
    *   Docker & Docker Compose

## 🚀 Como Executar o Projeto Localmente

### Pré-requisitos

*   Docker
*   Docker Compose

### Passos para Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2.  **Crie o arquivo de variáveis de ambiente:**
    *   Crie um arquivo chamado `.env` na raiz do projeto.
    *   Copie o conteúdo do arquivo `env.example` (se você tiver um) ou adicione as seguintes variáveis:
        ```env
        SECRET_KEY='sua_chave_secreta_super_segura_aqui'
        DEBUG=True
        ALLOWED_HOSTS=localhost,127.0.0.1,web
        
        SQL_ENGINE=django.db.backends.postgresql
        SQL_DATABASE=clinic_db
        SQL_USER=clinic_user
        SQL_PASSWORD='testpassword123'
        SQL_HOST=db
        SQL_PORT=5432
        ```
    *   **Importante:** A `SECRET_KEY` deve ser uma string longa e aleatória.

3.  **Construa e suba os containers Docker:**
    ```bash
    docker-compose up --build -d
    ```
    O `--build` força a reconstrução das imagens, o que é importante na primeira vez ou após mudar dependências. O `-d` roda os containers em segundo plano.

4.  **Execute as migrações do Django:**
    O banco de dados será criado, mas as tabelas precisam ser aplicadas.
    ```bash
    docker-compose exec web python manage.py migrate
    ```

5.  **Crie um superusuário para acessar o Admin:**
    ```bash
    docker-compose exec web python manage.py createsuperuser
    ```
    Siga as instruções para criar seu usuário administrador.

6.  **(Opcional) Popule o banco de dados com dados iniciais:**
    *   Para popular o banco com dados fictícios (se você tiver o comando de gerenciamento `populate_db`):
        ```bash
    docker-compose exec web python manage.py populate_db
    ```
    *   Alternativamente, acesse o Django Admin (`http://localhost:8000/admin/`) com seu superusuário e cadastre Sintomas e Doenças manualmente.

### Acessando a Aplicação

*   **API Back-end:** `http://localhost:8000/api/clinic/`
*   **Documentação da API (Swagger):** `http://localhost:8000/api/docs/`
*   **Django Admin:** `http://localhost:8000/admin/`
*   **Front-end (se estiver usando Live Server):** Geralmente `http://127.0.0.1:5500/frontend/index.html`

## 🔮 Próximos Passos e Futuras Funcionalidades

*   **Refinar o Algoritmo de Diagnóstico:**
    *   Implementar um sistema de "pesos" para sintomas patognomônicos (altamente específicos).
    *   Considerar outros fatores como espécie, raça e idade do paciente no cálculo do score.
*   **Expandir Módulos:**
    *   Implementar o Módulo 4: Gerenciamento de Vacinação e Vermifugação com lembretes.
    *   Implementar a geração de documentos (receituários, atestados).

---
