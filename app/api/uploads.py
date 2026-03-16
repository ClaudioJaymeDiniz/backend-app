import cloudinary
import cloudinary.uploader
import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from dotenv import load_dotenv
from app.api.deps import get_current_user # Importamos o dependente de autenticação

load_dotenv()

# Configuração do Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

router = APIRouter(prefix="/uploads", tags=["Uploads (Nuvem)"])

@router.post("/image")
async def upload_image(
    file: UploadFile = File(...), 
    folder: str = "submissions",
    user = Depends(get_current_user) # Apenas usuários com JWT válido entram aqui
):
    """
    Realiza o upload de imagens para o Cloudinary de forma segura.
    Atende ao RNF 03 (Nuvem) e RNF de Segurança (Autenticação).
    """
    # 1. Validar extensões
    allowed_extensions = ["jpg", "jpeg", "png", "webp"]
    file_ext = file.filename.split(".")[-1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Formato de imagem inválido.")

    try:
        # 2. Enviar para o Cloudinary
        # Adicionamos tags para saber qual usuário fez o upload na plataforma deles
        result = cloudinary.uploader.upload(
            file.file,
            folder=f"smart_forms/{folder}",
            resource_type="image",
            tags=[f"user_{user.id}", "tcc_project"],
            quality="auto",
            fetch_format="auto"
        )

        # 3. Retornar a URL segura
        return {"url": result.get("secure_url")}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")