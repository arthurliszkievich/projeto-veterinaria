# 🐾 ZoeVet - Sistema de Gestão Veterinária

> Sistema completo de gerenciamento veterinário com Django REST Framework e frontend moderno

[![Django](https://img.shields.io/badge/Django-5.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)

---

## 🚀 Início Rápido

### Backend (Terminal 1)
```powershell
cd C:\Users\arthu\projeto-veterinaria\projeto-veterinaria
.\venv\Scripts\Activate.ps1
python manage.py runserver
```
✅ Backend: http://127.0.0.1:8000/

### Frontend (Terminal 2)
```powershell
cd C:\Users\arthu\projeto-veterinaria\projeto-veterinaria\frontend
python -m http.server 3000
```
✅ Frontend: http://localhost:3000/index.html

---

## 📚 Documentação

| Documento | Descrição | Acesso |
|-----------|-----------|--------|
| 📘 **Guia do Usuário** | Como usar o ZoeVet | [docs/GUIA_USUARIO.md](docs/GUIA_USUARIO.md) |
| ⚙️ **Guia Técnico** | Arquitetura e detalhes | [docs/GUIA_TECNICO.md](docs/GUIA_TECNICO.md) |
| ⚡ **Comandos Rápidos** | Referência de comandos | [docs/COMANDOS_RAPIDOS.md](docs/COMANDOS_RAPIDOS.md) |
| 📝 **Changelog** | Histórico de mudanças | [docs/CHANGELOG.md](docs/CHANGELOG.md) |

---

## ✨ Funcionalidades Principais

### 👥 3 Tipos de Usuário
- **👤 Cliente**: Acompanhar pets e consultas
- **👨‍⚕️ Funcionário**: Cadastros e consultas
- **� Gerente**: Gestão completa

### 🔐 Autenticação
- Login separado por perfil
- Registro de novos usuários
- JWT tokens seguros

### 📋 Gestão Completa
- Cadastro de tutores e pacientes
- Registro de consultas veterinárias
- Sistema de diagnóstico auxiliar
- Histórico completo

---

## 🛠️ Tecnologias

**Backend:** Django 5.2.7 • DRF • JWT • PostgreSQL/SQLite  
**Frontend:** HTML5 • CSS3 • JavaScript ES2021  
**Tools:** ESLint • Prettier • Git

---

## 📁 Estrutura

```
projeto-veterinaria/
├── clinic/           # App Django (API)
├── config/           # Configurações
├── frontend/         # Interface web
├── docs/             # Documentação
└── requirements.txt  # Dependências
```

---

## � Links Rápidos

### Backend
- 🌐 API: http://127.0.0.1:8000/api/v1/
- 👨‍💼 Admin: http://127.0.0.1:8000/admin/
- 📖 Docs: http://127.0.0.1:8000/api/v1/docs/

### Frontend  
- 🏠 Início: http://localhost:3000/index.html
- 📊 Dashboard: http://localhost:3000/dashboard.html

---

## � Status

✅ **31 testes** passando  
✅ **Frontend** responsivo  
✅ **API** completa  
✅ **Docs** atualizadas

---

**Desenvolvido com ❤️**  
*ZoeVet - Sistema de Gestão Veterinária*
