'''
# run.py (na raiz do projeto /backend)
import uvicorn
import os
from dotenv import load_dotenv

# Agora ele busca o .env na mesma pasta onde o run.py está (Raiz)
load_dotenv()

if __name__ == "__main__":
    # Pega a porta do .env ou usa 8001 como fallback
    port = int(os.getenv("PORT", 8001)) 
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"📂 Configurações carregadas da raiz do projeto.")
    print(f"🚀 Iniciando servidor em http://{host}:{port}")
    
    uvicorn.run(
        "app.main:app", 
        host=host, 
        port=port, 
        reload=True,
        reload_excludes=["venv/*", "**/__pycache__/*"]
    )'''




    # run.py
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8001))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"🚀 Iniciando servidor em http://{host}:{port}")
    
    uvicorn.run(
        "app.main:app", 
        host=host, 
        port=port, 
        reload=True,
        # ESTA LINHA É A CHAVE:
        reload_excludes=["venv/*", "**/__pycache__/*", "prisma/*"]
    )