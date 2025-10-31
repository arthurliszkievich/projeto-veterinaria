# 🐾 ZoeVet - Sistema de Gestão Veterinária

> Sistema completo de gerenciamento veterinário com Django REST Framework e algoritmo inteligente de diagnóstico para pequenos animais.

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-20.10+-blue.svg)](https://www.docker.com/)

---

## 📖 Sobre o Projeto

Este projeto é um **sistema de gestão veterinária** desenvolvido com **Django** e **Django REST Framework**, projetado para auxiliar no diagnóstico clínico de pequenos animais. A principal funcionalidade é um sistema inteligente, apelidado de **"Akinator Veterinário"**, que sugere possíveis diagnósticos com base nos sintomas apresentados pelo paciente durante uma consulta.

O back-end robusto gerencia todas as entidades (tutores, pacientes, veterinários, sintomas, doenças e consultas) e expõe uma API RESTful completa. Um front-end responsivo está em desenvolvimento para consumir essa API e fornecer uma interface intuitiva para o registro de consultas e visualização das sugestões de diagnóstico.

---

## ✨ Funcionalidades Principais

### 🔐 Autenticação e Perfis de Usuário

- **3 Tipos de Usuário:**
  - 👤 **Cliente**: Acompanhar pets e consultas
  - 👨‍⚕️ **Veterinário**: Cadastros, consultas e diagnósticos
  - 👨‍💼 **Gerente**: Gestão completa do sistema

- Login separado por perfil
- Registro de novos usuários
- JWT tokens seguros com `djangorestframework-simplejwt`

### 📋 API RESTful Completa

- **CRUDs para todas as entidades principais:**
  - Tutores
  - Pacientes (Animais)
  - Veterinários
  - Sintomas
  - Doenças
  - Consultas

### 🧠 Sistema de Suporte a Diagnóstico ("Akinator Veterinário")

- Análise automática de sintomas ao registrar consulta
- Cálculo de **score de proporção** para cada doença
- Indicação da relevância da correspondência dos sintomas
- Lista de diagnósticos suspeitos ordenada por probabilidade
- Algoritmo preparado para expansão (pesos, fatores biológicos como espécie, raça, idade)

### 🎯 Recursos Adicionais

- **Filtros e Paginação:** Consumo eficiente de dados
- **Testes Automatizados:** Suíte robusta com `pytest` e `factory_boy`
- **Documentação da API:** Swagger UI / Redoc com `drf-spectacular`
- **Containerização:** Docker & Docker Compose para ambiente consistente e reproduzível

### 📱 Front-end (em desenvolvimento)

- Interface intuitiva para registrar novas consultas
- Carregamento dinâmico de sintomas com paginação
- Seleção de checkboxes para sintomas apresentados
- Exibição de diagnósticos sugeridos com scores

---

## 🛠️ Tecnologias Utilizadas

| Camada | Tecnologias |
|--------|------------|
| **Backend** | Python 3.10+ • Django 5.2.7 • Django REST Framework • PostgreSQL • Gunicorn |
| **Autenticação** | JWT • `djangorestframework-simplejwt` |
| **API Docs** | `drf-spectacular` (Swagger UI / Redoc) |
| **Testes** | `pytest` • `factory_boy` • `Faker` |
| **Frontend** | HTML5 • CSS3 • JavaScript ES6+ (`async/await`, `fetch`) |
| **DevOps** | Docker • Docker Compose |

---

## 🚀 Como Executar o Projeto

### Pré-requisitos

- Docker 20.10+
- Docker Compose 1.29+
- Git

### Opção 1: Com Docker (Recomendado)

#### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

#### 2. Crie o arquivo de variáveis de ambiente (`.env`)

Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:

```env
SECRET_KEY='sua_chave_secreta_super_segura_aqui_min_32_caracteres'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,web

SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=clinic_db
SQL_USER=clinic_user
SQL_PASSWORD='testpassword123'
SQL_HOST=db
SQL_PORT=5432
```

⚠️ **Importante:** A `SECRET_KEY` deve ser uma string longa e aleatória (mínimo 32 caracteres).

#### 3. Construa e suba os containers

```bash
docker-compose up --build -d
```

O `--build` força a reconstrução das imagens. O `-d` roda os containers em segundo plano.

#### 4. Execute as migrações do Django

```bash
docker-compose exec web python manage.py migrate
```

#### 5. Crie um superusuário para o Admin

```bash
docker-compose exec web python manage.py createsuperuser
```

Siga as instruções para criar seu usuário administrador.

#### 6. (Opcional) Popule o banco com dados iniciais

```bash
docker-compose exec web python manage.py populate_db
```

Alternativamente, acesse o Django Admin e cadastre sintomas e doenças manualmente.

### Opção 2: Desenvolvimento Local (sem Docker)

#### 1. Clone e navegue para o projeto

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

#### 2. Crie e ative um ambiente virtual

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

#### 4. Configure o banco de dados

```bash
python manage.py migrate
```

#### 5. Crie um superusuário

```bash
python manage.py createsuperuser
```

#### 6. Inicie o servidor de desenvolvimento

```bash
python manage.py runserver
```

O backend estará disponível em `http://127.0.0.1:8000/`

#### 7. (Em outro terminal) Inicie o servidor frontend

```bash
cd frontend
python -m http.server 3000
```

O frontend estará disponível em `http://localhost:3000/index.html`

---

## 🔗 Acessando a Aplicação

### Com Docker

| Serviço | URL |
|---------|-----|
| 🌐 **API Backend** | http://localhost:8000/api/clinic/ |
| 📖 **Documentação API (Swagger)** | http://localhost:8000/api/docs/ |
| 📚 **Redoc** | http://localhost:8000/api/redoc/ |
| 👨‍💼 **Django Admin** | http://localhost:8000/admin/ |
| 📱 **Frontend** | http://localhost:3000/index.html (via Live Server) |

### Desenvolvimento Local

| Serviço | URL |
|---------|-----|
| 🌐 **API Backend** | http://127.0.0.1:8000/api/clinic/ |
| 📖 **Documentação API** | http://127.0.0.1:8000/api/docs/ |
| 👨‍💼 **Django Admin** | http://127.0.0.1:8000/admin/ |
| 📱 **Frontend** | http://localhost:3000/index.html |

---

## 📁 Estrutura do Projeto

```
projeto-veterinaria/
├── clinic/                    # App Django (modelos, views, serializers)
│   ├── models.py             # Modelos: Tutor, Paciente, Consulta, etc.
│   ├── views.py              # ViewSets da API
│   ├── serializers.py        # Serializers para os modelos
│   ├── permissions.py        # Permissões customizadas
│   └── tests/                # Testes unitários
├── config/                    # Configurações do Django
│   ├── settings.py           # Configurações principais
│   ├── urls.py               # URLs raiz
│   └── wsgi.py               # WSGI para produção
├── frontend/                  # Interface web
│   ├── index.html            # Página de login
│   ├── dashboard.html        # Dashboard principal
│   ├── consulta.html         # Página de nova consulta
│   ├── css/                  # Estilos
│   └── js/                   # Scripts frontend
├── docs/                      # Documentação
│   ├── GUIA_USUARIO.md       # Guia do usuário
│   ├── GUIA_TECNICO.md       # Arquitetura técnica
│   ├── COMANDOS_RAPIDOS.md   # Referência de comandos
│   └── CHANGELOG.md          # Histórico de mudanças
├── requirements.txt           # Dependências Python
├── docker-compose.yml        # Configuração Docker Compose
├── Dockerfile                # Imagem Docker da aplicação
├── .env.example              # Template de variáveis de ambiente
└── README.md                 # Este arquivo
```

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| 📘 **[Guia do Usuário](docs/GUIA_USUARIO.md)** | Como usar o ZoeVet |
| ⚙️ **[Guia Técnico](docs/GUIA_TECNICO.md)** | Arquitetura e detalhes de implementação |
| ⚡ **[Comandos Rápidos](docs/COMANDOS_RAPIDOS.md)** | Referência de comandos úteis |
| 📝 **[Changelog](docs/CHANGELOG.md)** | Histórico de mudanças |

---

## ✅ Status Atual

- ✅ **31+ testes** passando
- ✅ **Frontend** responsivo
- ✅ **API RESTful** completa com CRUDs
- ✅ **Sistema de diagnóstico** funcional
- ✅ **Autenticação JWT** implementada
- ✅ **Documentação** atualizada
- 🚀 **Docker** totalmente configurado

---

## 🔮 Próximos Passos e Futuras Funcionalidades

### Curto Prazo

- Refinar o **Algoritmo de Diagnóstico**:
  - Implementar sistema de "pesos" para sintomas patognomônicos
  - Considerar fatores: espécie, raça, idade no score
  - Validação cruzada com especialistas

### Médio Prazo

- **Módulo 4: Vacinação e Vermifugação**
  - Gerenciamento de campanhas
  - Sistema de lembretes automáticos
  - Relatórios de vacinação

- **Geração de Documentos**
  - Receituários
  - Atestados
  - Relatórios de consultas

### Longo Prazo

- **Dashboard Analítico**
  - Estatísticas de diagnósticos
  - Relatórios por período
  - Análise de tendências

- **Integração com Sistemas Externos**
  - API de marcação de agendamentos
  - Integração com farmácias
  - Notificações via SMS/Email

---

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

---

## 📞 Suporte

Para dúvidas, abra uma issue ou entre em contato através do email do projeto.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

**Desenvolvido com ❤️**  
*ZoeVet - Sistema de Gestão Veterinária*

Última atualização: 31 de outubro de 2025
