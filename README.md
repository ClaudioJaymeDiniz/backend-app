# 📋 Smart Forms - Backend

Sistema de gerenciamento de formulários customizáveis com sincronização offline e arquitetura limpa.

## 🚀 Tecnologias Utilizadas

* **Linguagem:** Python 3.12+
* **Framework:** FastAPI
* **ORM:** Prisma Client Python (v5.17.0)
* **Banco de Dados:** PostgreSQL (Supabase)


---

## 🛠️ Pré-requisitos

Antes de começar, você precisará ter instalado em sua máquina:
1.  **Python 3.10+** e `pip`
2.  **Node.js** (para a CLI do Prisma)
3.  **Venv** (Ambiente virtual do Python)

---

## 🏃 Como Rodar o Projeto

### 1. Clonar e Configurar Ambiente
```bash
# Entre na pasta do backend
cd app/backend

# Crie o ambiente virtual
python3 -m venv venv

# Ative o ambiente virtual Linux
source venv/bin/activate
# Ative o ambiente virtual Windows
venv\Scripts\activate

# Instale as dependências Python
pip install -r requirements.txt

2. Configurar Variáveis de Ambiente

Crie um arquivo .env na raiz do diretório backend e adicione sua URL do banco de dados:
DATABASE_URL="postgresql://postgres:[SENHA]@[HOST]:5432/postgres"
ENV="development"

# Configurações do Servidor
PORT=8001
HOST=0.0.0.0

# Dica: Gere uma chave aleatória com: openssl rand -hex 32
SECRET_KEY=""
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 horas

3. Configurar o Banco de Dados (Prisma)

Como utilizamos o Prisma para gerenciar o schema, execute os comandos abaixo para sincronizar as tabelas e gerar o cliente:

3. Configurar o Banco de Dados (Prisma)

Como utilizamos o Prisma para gerenciar o schema, execute os comandos abaixo para sincronizar as tabelas e gerar o cliente:
# Instalar dependências de desenvolvimento do Node
npm install

# Sincronizar o schema com o banco de dados (Supabase/Postgres)
npx prisma@5.17.0 db push

# Gerar o cliente Python
npx prisma@5.17.0 generate

4. Iniciar o Servidor

python run.py