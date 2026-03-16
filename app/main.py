from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.prisma_client import db
from app.api.auth import router as auth_router
from app.api.projects import router as projects_router
from app.api.forms import router as forms_router
from app.api.submissions import router as submissions_router # Importe correto
# from fastapi.staticfiles import StaticFiles
import os
from app.api.uploads import router as uploads_router




@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- STARTUP ---
    # Conecta o cliente Prisma (O db push deixamos para rodar manual no terminal)
    await db.connect()
    print("🚀 API iniciada e banco conectado.")
    
    yield  # Aplicação em execução
    
    # --- SHUTDOWN ---
    await db.disconnect()
    print("🛑 Conexão com o banco encerrada.")

app = FastAPI(
    title="Smart Forms API",
    description="Backend para gestão de formulários dinâmicos com sincronização offline e analytics.",
    version="1.0.0",
    contact={
        "name": "Claudio Jayme",
        "url": "https://github.com/ClaudioJaymeDiniz",
    },
)

# --- CONFIGURAÇÃO DE CORS ---
# Essencial para o seu app React Native conseguir conversar com a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, substitua pelo domínio do seu app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Smart Forms API - Sistema de Formulários Inteligentes",
        "docs": "/docs"
    }

# --- REGISTRO DE ROTAS ---
app.include_router(auth_router)
app.include_router(projects_router)
app.include_router(forms_router)
app.include_router(submissions_router) # Adicionado o router de submissões
app.include_router(uploads_router) # Adicionado o router de uploads


