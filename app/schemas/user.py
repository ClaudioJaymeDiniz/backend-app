'''
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

# O que é comum a todos
class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

# O que recebemos no Cadastro
class UserCreate(UserBase):
    password: str

# O que devolvemos para o Frontend (Sem a senha!)
class UserResponse(UserBase):
    id: str
    createdAt: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None # Caso ele queira trocar a senha
    '''

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