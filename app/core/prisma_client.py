# app/prisma_client.py
import os
from prisma import Prisma
from dotenv import load_dotenv

# Isso garante que ele ache o .env mesmo que você rode o comando de pastas diferentes
load_dotenv()

# Pegamos a URL e validamos se ela existe
database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("A variável DATABASE_URL não foi encontrada no arquivo .env")

db = Prisma(
    datasource={
        'url': database_url
    }
)

async def connect_db():
    # O check 'is_connected' evita erros de "Connection already open"
    if not db.is_connected():
        await db.connect()

async def disconnect_db():
    if db.is_connected():
        await db.disconnect()