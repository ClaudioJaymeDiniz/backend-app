from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.core.security import verify_password, create_access_token
from app.api.deps import get_current_user
from app.schemas.user import UserUpdate
import uuid
from datetime import datetime, timedelta
from app.schemas.user import PasswordRecoveryRequest, PasswordReset


router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/register", response_model=UserResponse)
async def register(user_in: UserCreate):
    user_exists = await UserService.get_by_email(user_in.email)
    if user_exists:
        raise HTTPException(status_code=400, detail="Usuário já cadastrado.")
    return await UserService.create_user(user_in)

@router.post("/login")
async def login(credentials: OAuth2PasswordRequestForm = Depends()):
    user = await UserService.get_by_email(credentials.username)
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
    
    token = create_access_token(data={"sub": user.id, "email": user.email})
    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """Retorna os dados do usuário dono do token atual."""
    return current_user

@router.patch("/me", response_model=UserResponse)
async def update_me(
    user_in: UserUpdate, 
    current_user = Depends(get_current_user)
):
    """Atualiza os dados do usuário logado."""
    return await UserService.update_user(current_user.id, user_in)

@router.post("/recover-password")
async def recover_password(data: PasswordRecoveryRequest):
    user = await UserService.get_by_email(data.email)
    
    if not user:
        # Por segurança, não confirmamos se o e-mail existe ou não
        return {"message": "Se o e-mail existir, um link será enviado."}

    # Gerar um token único (UUID) e salvar no globalMetadata ou em uma nova tabela
    reset_token = str(uuid.uuid4())
    
    # Vamos salvar o token e a expiração no globalMetadata do usuário (estratégia rápida)
    expires = datetime.now() + timedelta(hours=1)
    metadata = user.globalMetadata or {}
    metadata["reset_token"] = reset_token
    metadata["reset_token_expires"] = expires.isoformat()

    await UserService.update_user(user.id, UserUpdate(globalMetadata=metadata))

    # DEBUG: No seu terminal do Linux Mint aparecerá o link
    print(f"--- LINK DE RECUPERAÇÃO PARA {user.email} ---")
    print(f"http://localhost:3000/reset-password?token={reset_token}")
    print("---------------------------------------------")

    return {"message": "Link de recuperação enviado com sucesso."}

# ROTA 2: Resetar a Senha de fato
@router.post("/reset-password")
async def reset_password(data: PasswordReset):
    # Buscar usuário que tenha esse token no metadata
    # Nota: Em produção, o ideal é ter uma tabela 'PasswordReset' no Prisma
    user = await db.user.find_first(
        where={
            "globalMetadata": {
                "path": ["reset_token"],
                "equals": data.token
            }
        }
    )

    if not user:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")

    # Validar expiração
    expires_str = user.globalMetadata.get("reset_token_expires")
    if datetime.fromisoformat(expires_str) < datetime.now():
        raise HTTPException(status_code=400, detail="Token expirado.")

    # Atualizar senha e limpar o token
    from app.core.security import get_password_hash
    hashed_password = get_password_hash(data.new_password)
    
    metadata = user.globalMetadata
    del metadata["reset_token"]
    del metadata["reset_token_expires"]

    await db.user.update(
        where={"id": user.id},
        data={
            "password": hashed_password,
            "globalMetadata": metadata
        }
    )

    return {"message": "Senha alterada com sucesso!"}