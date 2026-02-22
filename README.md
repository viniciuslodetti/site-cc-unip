# 🎓 Sistema Turma UNIP

Sistema de gerenciamento de turma da UNIP — controle de alunos, camisas, esportes e avisos.

---

## 🚀 Como fazer o Deploy no Render.com (Gratuito)

### Pré-requisitos
- Conta no [GitHub](https://github.com)
- Conta no [Render.com](https://render.com) (pode criar com a conta do GitHub)

---

### Passo 1 — Subir o projeto no GitHub

No terminal (dentro da pasta do projeto):

```bash
git init
git add .
git commit -m "primeiro commit"
git branch -M main
git remote add origin https://github.com/SEU_USUARIO/SEU_REPOSITORIO.git
git push -u origin main
```

---

### Passo 2 — Criar o banco de dados PostgreSQL no Render

1. Acesse [render.com](https://render.com) e faça login
2. Clique em **"New +"** → **"PostgreSQL"**
3. Preencha:
   - **Name:** `turma-unip-db`
   - **Plan:** Free
4. Clique em **"Create Database"**
5. Aguarde criar e **copie o campo "Internal Database URL"**

---

### Passo 3 — Criar o Web Service no Render

1. Clique em **"New +"** → **"Web Service"**
2. Conecte ao seu repositório GitHub
3. Preencha:
   - **Name:** `sistema-turma-unip`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Plan:** Free
4. Em **"Environment Variables"**, adicione:

| Chave | Valor |
|-------|-------|
| `DATABASE_URL` | (cole a URL do PostgreSQL copiada no Passo 2) |
| `SECRET_KEY` | (gere uma chave aleatória forte) |
| `JWT_SECRET_KEY` | (gere outra chave aleatória forte) |
| `UPLOAD_FOLDER` | `static/uploads` |
| `MAX_CONTENT_LENGTH` | `16777216` |
| `FLASK_ENV` | `production` |

5. Clique em **"Create Web Service"**

---

### Passo 4 — Acessar o site

Após o deploy (2-4 minutos), o Render fornece um link:
```
https://sistema-turma-unip.onrender.com
```

**Login padrão (admin):**
- RA: `admin`
- Senha: `admin123`

> ⚠️ **Altere a senha do admin após o primeiro acesso!**

---

## 💻 Rodar Localmente

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar o servidor
python app.py
```

Acesse: http://localhost:5000

---

## 📁 Estrutura do Projeto

```
.
├── app.py              # Backend Flask (API + servidor - Ponto de Entrada)
├── requirements.txt    # Dependências Python
├── .env                # Variáveis de ambiente (local, NÃO deve ser postado no Git)
├── .gitignore          # Arquivos ignorados pelo Git
├── instance/           # Banco de dados SQLite local
├── static/             # Arquivos do Frontend
│   ├── index.html      # Interface principal
│   ├── app.js          # Lógica do frontend
│   ├── styles.css      # Estilos CSS
│   └── uploads/        # Pasta para imagens postadas
└── scripts/            # Scripts utilitários de reparo e manutenção
```

---

## 🛠️ Tecnologias

- **Backend:** Flask, SQLAlchemy, JWT
- **Banco de dados:** SQLite (local) / PostgreSQL (produção)
- **Frontend:** HTML, CSS, JavaScript puro
- **Deploy:** Render.com + Gunicorn
