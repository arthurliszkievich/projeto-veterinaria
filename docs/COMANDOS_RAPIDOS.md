# ⚡ COMANDOS RÁPIDOS - Sistema Veterinário

## 🚀 INICIAR O SISTEMA

### 1️⃣ BACKEND (Terminal 1)
```powershell
# Ativar venv + Rodar Django
& C:/Users/arthu/projeto-veterinaria/projeto-veterinaria/venv/Scripts/Activate.ps1
python manage.py runserver
```
✅ Backend rodando em: http://127.0.0.1:8000/

### 2️⃣ FRONTEND (Terminal 2)
```powershell
# Entrar na pasta + Iniciar servidor
cd C:/Users/arthu/projeto-veterinaria/projeto-veterinaria/frontend
python -m http.server 3000
```
✅ Frontend rodando em: http://localhost:3000/login.html

---

## 🔐 LOGIN

**URL:** http://localhost:3000/login.html
- **Usuário:** admin
- **Senha:** (sua senha)

---

## 📝 DESENVOLVIMENTO

### Formatar Código
```powershell
npm run format        # Prettier - HTML, CSS, JS
```

### Verificar Erros
```powershell
npm run lint          # ESLint - Verificar
npm run lint:fix      # ESLint - Corrigir
```

### Testes Backend
```powershell
python manage.py test
```

---

## 📍 URLS IMPORTANTES

### Backend:
- API Base: http://127.0.0.1:8000/api/v1/
- Admin: http://127.0.0.1:8000/admin/
- Swagger Docs: http://127.0.0.1:8000/api/v1/docs/
- ReDoc: http://127.0.0.1:8000/api/v1/redoc/

### Frontend:
- Login: http://localhost:3000/login.html
- Registro: http://localhost:3000/registro.html
- Dashboard: http://localhost:3000/dashboard.html
- Novo Tutor: http://localhost:3000/novo-tutor.html
- Novo Paciente: http://localhost:3000/novo-paciente.html
- Pacientes: http://localhost:3000/pacientes.html
- Consulta: http://localhost:3000/consulta.html

---

## 🛑 PARAR O SISTEMA

- **Backend:** `CTRL + BREAK` ou `CTRL + C`
- **Frontend:** `CTRL + C`

---

## 💾 BANCO DE DADOS

### Criar Migrações
```powershell
python manage.py makemigrations
```

### Aplicar Migrações
```powershell
python manage.py migrate
```

### Popular Banco (se houver comando)
```powershell
python manage.py populate_db
```

### Criar Superusuário
```powershell
python manage.py createsuperuser
```

---

## 📦 DEPENDÊNCIAS

### Instalar/Atualizar Python
```powershell
pip install -r requirements.txt
```

### Instalar/Atualizar Node
```powershell
npm install
```

---

## 🔍 DEBUG

### Logs Django
- Console onde está rodando `python manage.py runserver`
- Arquivo: `django_logs.log` (se configurado)

### Erros Frontend
- F12 no navegador → Console
- F12 → Network (para ver chamadas à API)

---

## ✅ CHECKLIST INICIAL

- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Migrações aplicadas (`python manage.py migrate`)
- [ ] Superusuário criado
- [ ] Backend rodando (porta 8000)
- [ ] Frontend rodando (porta 3000)
- [ ] Login funciona
- [ ] Cadastro de tutor funciona
- [ ] Cadastro de paciente funciona

---

**Versão:** 2.0  
**Última atualização:** 29/10/2025
