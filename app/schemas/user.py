from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from datetime import datetime

# Base: campos comuns
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    provider: str = "local"

# Entrada: O que recebemos no registro
class UserCreate(UserBase):
    password: str

# Atualização: O que o usuário pode mudar
class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None
    globalMetadata: Optional[dict] = None

# Saída: O que a API responde (Nunca inclui a senha!)
class UserResponse(UserBase):
    id: str
    createdAt: datetime
    globalMetadata: Optional[Any] = None

    class Config:
        from_attributes = True

# Recuperar senha
class PasswordRecoveryRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str

class UserSimple(BaseModel):
    id: str
    name: Optional[str] = None
    email: EmailStr

    class Config:
        from_attributes = True