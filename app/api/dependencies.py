from fastapi import FastAPI
from app.core.prisma_client import connect_db, disconnect_db

app = FastAPI(title="Smart Forms API")

@app.on_event("startup")
async def startup():
    await connect_db()

@app.on_event("shutdown")
async def shutdown():
    await disconnect_db()

@app.get("/")
def read_root():
    return {"status": "Online", "msg": "Sistema de Formulários Inteligentes"}