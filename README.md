# 🐾 ZoeVet - Sistema de Gestão Veterinária com Suporte à Decisão Clínica

> Sistema de gerenciamento veterinário arquitetado com **Clean Architecture**, **SOLID** e **Service Layer Pattern**, implementando um motor de diagnóstico baseado em **F1-Score** para sugestão inteligente de doenças.

[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.2.1-green.svg)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.16.0-red.svg)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![Tests](https://img.shields.io/badge/Tests-13%20Passed%20%7C%20100%25%20Coverage-brightgreen.svg)](clinic/tests/)
[![Code Style](https://img.shields.io/badge/Code%20Style-SOLID%20%7C%20Clean%20Architecture-purple.svg)]()

---

## 🎯 Sobre o Projeto

Desenvolvi o **ZoeVet** como um sistema de gestão veterinária com foco em **qualidade de código** e **arquitetura escalável**. O projeto foi recentemente refatorado para seguir princípios de **Clean Architecture** e **SOLID**, com toda a lógica de negócio isolada em uma **Service Layer** dedicada.

A funcionalidade principal é um **motor de diagnóstico veterinário** (apelidado internamente de "Akinator Veterinário") que utiliza um algoritmo de **F1-Score** para balancear **cobertura** e **precisão** ao sugerir doenças baseadas nos sintomas apresentados durante uma consulta. Tomei a decisão de isolar completamente essa lógica em um serviço puro (`DiagnosticoService`) para garantir:

- ✅ **Testabilidade**: 100% de cobertura com testes unitários usando pytest
- ✅ **Manutenibilidade**: Lógica de negócio separada das camadas de apresentação e persistência
- ✅ **Escalabilidade**: Possibilidade de expandir o algoritmo (ML, pesos adaptativos) sem impactar outras camadas
- ✅ **Reusabilidade**: Serviços podem ser consumidos por múltiplos endpoints ou interfaces

---

## 🏗️ Technical Deep Dive - Documentação Técnica

Se você é um recrutador técnico ou desenvolvedor interessado em **como eu pensei e implementei a arquitetura**, criei documentação completa em primeira pessoa explicando minhas decisões:

| 📄 Documento | 🎯 O que você vai encontrar |
|-------------|---------------------------|
| **[🔧 Refatoração Service Layer](docs/REFATORACAO_SERVICE_LAYER.md)** | Como identifiquei code smells (Fat ViewSets, validação em Serializers), minha estratégia de refatoração e as métricas que alcancei (67% de redução no código das Views) |
| **[🏛️ Arquitetura Service Layer](docs/ARQUITETURA_SERVICE_LAYER.md)** | Diagramas de fluxo, decisões de design (por que DI manual e não frameworks), estrutura de pastas e responsabilidades de cada camada |
| **[🧪 Relatório de Testes](docs/RELATORIO_TESTES.md)** | Estratégia de testes, explicação de cada um dos 13 testes unitários, demonstrações práticas e cobertura de 100% da Service Layer |

**💡 Por que essa documentação é diferente?** Não é apenas uma descrição técnica genérica. Explico o **porquê** de cada decisão arquitetural, os **trade-offs** considerados e os **resultados mensuráveis** alcançados. Ideal para demonstrar senioridade técnica e capacidade de comunicação.

---

## ✨ Funcionalidades Principais

### 🏛️ Arquitetura em Camadas (Clean Architecture)

Refatorei o projeto seguindo **princípios SOLID** e **Service Layer Pattern**:

```
┌─────────────────────────────────────────┐
│   Views (Apresentação)                  │  ← ViewSets minimalistas
│   ↓ apenas orquestram requests          │
├─────────────────────────────────────────┤
│   Serializers (Validação de Entrada)    │  ← Validam formato/tipos
│   ↓ sem lógica de negócio               │
├─────────────────────────────────────────┤
│   Services (Lógica de Negócio) ⭐       │  ← Toda regra de negócio aqui
│   • DiagnosticoService                  │     • 100% testado
│   • ConsultaService                     │     • Reutilizável
│   • TutorService                        │     • Sem dependência de Django
├─────────────────────────────────────────┤
│   Models (Persistência)                 │  ← Apenas definições de tabelas
└─────────────────────────────────────────┘
```

**Por que essa arquitetura?**
- **Testabilidade**: Services não dependem do Django, posso testá-los isoladamente
- **Manutenibilidade**: Se mudo uma regra de negócio, sei exatamente onde alterar
- **Reutilização**: Mesma lógica pode ser usada em APIs, CLIs, background jobs
- **Onboarding**: Novos devs entendem rapidamente a responsabilidade de cada camada

### 🔐 Autenticação e Perfis de Usuário

- **3 Tipos de Usuário:**
  - 👤 **Cliente**: Acompanhar pets e consultas
  - 👨‍⚕️ **Veterinário**: Cadastros, consultas e diagnósticos
  - 👨‍💼 **Gerente**: Gestão completa do sistema

- Login separado por perfil com JWT tokens seguros (`djangorestframework-simplejwt`)

### 📋 API RESTful Completa

API desenvolvida com **Django REST Framework 3.16.0**, seguindo convenções RESTful:

- **CRUDs completos**: Tutores, Pacientes, Veterinários, Sintomas, Doenças, Consultas
- **Filtros e Paginação**: Performance otimizada para grandes volumes de dados
- **Documentação automática**: Swagger UI integrado via drf-spectacular

### 🧪 Testes Unitários com 100% de Cobertura

Implementei **13 testes unitários** cobrindo toda a Service Layer usando **pytest** e **factory_boy**:

```bash
$ pytest clinic/tests/ -v

clinic/tests/test_diagnostico_service.py::test_diagnostico_sem_sintomas PASSED
clinic/tests/test_diagnostico_service.py::test_diagnostico_com_match_perfeito PASSED
clinic/tests/test_diagnostico_service.py::test_diagnostico_com_multiplas_doencas PASSED
... [13 testes] ...

============ 13 passed in 0.42s ============
```

**Decisões de Testing:**
- **Factories**: Uso de `factory_boy` para criar fixtures consistentes
- **Isolamento**: Cada teste cria seu próprio conjunto de dados
- **Casos de borda**: Cenários extremos (sem sintomas, match perfeito, doenças sem sintomas)

### 🐳 Ambiente Docker Pronto para Produção

Containerização completa com **Docker** e **Docker Compose** para garantir consistência entre ambientes:

### 🧠 Motor de Diagnóstico com F1-Score (Principal Diferencial)

Implementei um **algoritmo de suporte à decisão clínica** que analisa os sintomas apresentados durante uma consulta e sugere doenças compatíveis com **score de confiança percentual**.

**Decisões Técnicas:**
- **Algoritmo F1-Score**: Escolhi usar a média harmônica entre **cobertura** (quantos sintomas da doença estão presentes no paciente) e **precisão** (quantos sintomas do paciente correspondem à doença) para evitar viés em doenças com poucos ou muitos sintomas
- **Isolamento em Service Layer**: Toda a lógica está no `DiagnosticoService`, facilitando testes unitários e futuras melhorias (como adicionar Machine Learning)
- **Extensibilidade**: A arquitetura permite facilmente adicionar pesos por sintoma, fatores epidemiológicos (espécie, raça, idade) ou integrar modelos de ML

**Exemplo de Output:**
```json
{
  "diagnosticos_suspeitos": [
    {"nome": "Pancreatite", "porcentagem": "66.9%", "score": 0.669},
    {"nome": "Gastroenterite", "porcentagem": "54.2%", "score": 0.542}
  ]
}
```

### 🐳 Ambiente Docker Pronto para Produção

Containerização completa com **Docker** e **Docker Compose** para garantir consistência entre ambientes:

- Dockerfile otimizado para Python 3.12
- Docker Compose com serviços web + PostgreSQL
- Hot-reload para desenvolvimento
- Scripts de inicialização automatizados

---

## 🛠️ Stack Tecnológica

Escolhi as seguintes tecnologias por suas características de **produção-ready** e **comunidade ativa**:

| Categoria | Tecnologias | Por que escolhi |
|-----------|-------------|-----------------|
| **Backend** | Python 3.12 • Django 5.2.1 • DRF 3.16.0 | Ecossistema maduro, ótima documentação, batteries included |
| **Database** | PostgreSQL 16 • SQLite (dev) | ACID compliance, JSON fields, performance |
| **Testing** | pytest 9.0.2 • factory_boy 3.3.1 | Fixtures simples, asserts claros, plugins extensíveis |
| **DevOps** | Docker • Docker Compose | Paridade dev/prod, onboarding rápido |
| **Autenticação** | JWT • djangorestframework-simplejwt | Stateless, escalável, seguro |
| **API Docs** | drf-spectacular | OpenAPI 3.0, Swagger UI automático |

---

## 🚀 Como Executar o Projeto

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

## 📁 Estrutura do Projeto

### Pré-requisitos

- **Docker 20.10+** e **Docker Compose 1.29+**
- Git

### Instruções de Execução

**1. Clone o repositório**

```bash
git clone https://github.com/arthurliszkievich/projeto-veterinaria.git
cd projeto-veterinaria
```

**2. Configure variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY='sua-chave-secreta-django-minimo-50-caracteres'
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,web

SQL_ENGINE=django.db.backends.postgresql
SQL_DATABASE=zoevet_db
SQL_USER=zoevet_user
SQL_PASSWORD=sua_senha_segura
SQL_HOST=db
SQL_PORT=5432
```

**3. Suba os containers**

```bash
docker-compose up --build
```

**4. Execute as migrações e popule o banco**

Em outro terminal:

```bash
# Aplicar migrações
docker-compose exec web python manage.py migrate

# Criar superusuário
docker-compose exec web python manage.py createsuperuser

# Popular banco com sintomas e doenças (opcional)
docker-compose exec web python manage.py populate_db
```

**5. Acesse a aplicação**

| Serviço | URL |
|---------|-----|
| 🌐 **API Backend** | http://localhost:8000/api/clinic/ |
| 📖 **Swagger UI** | http://localhost:8000/api/docs/ |
| 👨‍💼 **Django Admin** | http://localhost:8000/admin/ |
| 📱 **Frontend** | http://localhost:8000/ |

### Executar Testes

```bash
# Rodar todos os testes
docker-compose exec web pytest

# Com verbosidade e coverage
docker-compose exec web pytest -v --cov=clinic/services

# Apenas testes do DiagnosticoService
docker-compose exec web pytest clinic/tests/test_diagnostico_service.py -v
```

---

## 📁 Estrutura do Projeto

---

## 📁 Estrutura do Projeto

```
projeto-veterinaria/
├── clinic/                           # Core App Django
│   ├── services/                     # ⭐ Service Layer (Lógica de Negócio)
│   │   ├── __init__.py
│   │   ├── diagnostico_service.py    # Algoritmo F1-Score
│   │   ├── consulta_service.py       # Orquestração de consultas
│   │   └── tutor_service.py          # Validação de CPF
│   ├── tests/                        # Testes Unitários (100% coverage)
│   │   ├── test_diagnostico_service.py
│   │   ├── test_consulta_service.py
│   │   └── test_tutor_service.py
│   ├── models.py                     # Modelos Django (Tutor, Paciente, etc.)
│   ├── views.py                      # ViewSets minimalistas
│   ├── serializers.py                # Validação de entrada/saída
│   └── factories.py                  # Factory Boy fixtures
├── docs/                             # 📚 Documentação Técnica
│   ├── REFATORACAO_SERVICE_LAYER.md  # Como refatorei o projeto
│   ├── ARQUITETURA_SERVICE_LAYER.md  # Decisões arquiteturais
│   └── RELATORIO_TESTES.md           # Estratégia de testes
├── frontend/                         # Interface HTML/CSS/JS
│   ├── consulta.html                 # Tela de nova consulta
│   ├── dashboard.html                # Dashboard principal
│   └── script.js                     # Lógica do frontend
├── config/                           # Configurações Django
│   ├── settings.py
│   └── urls.py
├── docker-compose.yml                # Orquestração de containers
├── Dockerfile                        # Imagem Docker
├── requirements.txt                  # Dependências Python
└── pytest.ini                        # Configuração de testes
```

---

## 📊 Métricas e Resultados

| Métrica | Valor | Contexto |
|---------|-------|----------|
| **Redução de Linhas nas Views** | 67% | De 150 para 50 linhas após mover lógica para Services |
| **Cobertura de Testes** | 100% | Todos os Services cobertos por testes unitários |
| **Número de Testes** | 13 | Cobertura de cenários normais e extremos |
| **Tempo de Execução dos Testes** | 0.42s | Testes rápidos graças ao isolamento |
| **Complexidade Ciclomática** | Baixa | Services com métodos focados e responsabilidades únicas |
| **Sintomas no Banco** | 24 | Expandido de 4 para melhor acurácia diagnóstica |
| **Doenças no Banco** | 17 | Expandido de 2 com associações corretas |

---

## 🎓 Conceitos Técnicos Aplicados

Este projeto demonstra conhecimento prático de:

- ✅ **Clean Architecture**: Separação clara de responsabilidades entre camadas
- ✅ **SOLID Principles**: Cada service tem uma responsabilidade única
- ✅ **Dependency Injection**: Services recebem dependências via construtor
- ✅ **Service Layer Pattern**: Lógica de negócio isolada e testável
- ✅ **Test-Driven Development**: 100% de cobertura na camada de negócio
- ✅ **Factory Pattern**: Uso de factory_boy para fixtures consistentes
- ✅ **RESTful API Design**: Endpoints seguindo convenções REST
- ✅ **Docker & Containerization**: Ambiente reproduzível e escalável
- ✅ **Algoritmos de Machine Learning**: F1-Score para balancear métricas
- ✅ **Git Flow**: Commits organizados por tópico com mensagens descritivas

---

## 🔮 Roadmap e Melhorias Futuras

### Curto Prazo
- [ ] Adicionar pesos adaptativos aos sintomas (ex: febre tem peso maior)
- [ ] Implementar cache com Redis para diagnósticos frequentes
- [ ] Adicionar logging estruturado com ELK Stack

### Médio Prazo
- [ ] Integrar modelo de Machine Learning (Random Forest ou XGBoost)
- [ ] Implementar sistema de feedback veterinário para melhorar algoritmo
- [ ] Adicionar gráficos interativos com Chart.js no frontend

### Longo Prazo
- [ ] Deploy em produção (AWS ECS ou Railway)
- [ ] Implementar CI/CD com GitHub Actions
- [ ] Adicionar monitoramento com Prometheus + Grafana

---

## 💼 Por Que Este Projeto Demonstra Senioridade?

1. **Não é CRUD simples**: Sistema de diagnóstico com algoritmo matemático justificado
2. **Arquitetura escalável**: Fácil adicionar novos algoritmos ou migrar para microsserviços
3. **Testes robustos**: 100% de cobertura não é apenas métrica, os testes são úteis
4. **Documentação excepcional**: Explico o "porquê" de cada decisão, não apenas o "como"
5. **Código limpo**: Seguir SOLID não é buzzword, apliquei na prática com justificativas
6. **Pensamento em produção**: Docker, variáveis de ambiente, migrations, logging

---

## 📞 Contato

**Arthur Liszkievich**  
📧 Email: [seu-email@example.com](mailto:seu-email@example.com)  
💼 LinkedIn: [linkedin.com/in/arthur-liszkievich](https://www.linkedin.com/in/arthur-liszkievich)  
🐙 GitHub: [github.com/arthurliszkievich](https://github.com/arthurliszkievich)

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

<div align="center">

**⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!**

*Desenvolvido com ❤️ e boas práticas de engenharia de software*

</div>

