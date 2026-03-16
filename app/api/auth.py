
'''
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from app.core.prisma_client import db
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticação"])

# Schemas de Entrada/Saída
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(user_data: UserCreate):
    # 1. Verificar se o usuário já existe
    user_exists = await db.user.find_unique(where={"email": user_data.email})
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este e-mail já está cadastrado."
        )
    
    # 2. Criar o hash da senha e salvar
    hashed_password = get_password_hash(user_data.password)
    new_user = await db.user.create(
        data={
            "email": user_data.email,
            "password": hashed_password,
            "name": user_data.name,
            "provider": "local" # Diferencia de Google/FB
        }
    )
    return {"message": "Usuário criado com sucesso", "user_id": new_user.id}

@router.post("/login")
async def login(credentials: OAuth2PasswordRequestForm = Depends()):
    # O Swagger envia o e-mail no campo 'username'
    user = await db.user.find_unique(where={"email": credentials.username})
    
    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos."
        )
    
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    
    # O Swagger EXIGE que o retorno tenha 'access_token' e 'token_type'
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    }'''

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserResponse
from app.services.user_service import UserService
from app.core.security import verify_password, create_access_token
from app.api.deps import get_current_user
from app.schemas.user import UserUpdate


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