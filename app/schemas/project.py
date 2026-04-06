from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import List, Optional
from app.schemas.user import UserSimple

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    isPublic: bool = False
    logoUrl: Optional[str] = None
    # Validamos se é uma cor hexadecimal básica (opcional, mas boa prática)
    themeColor: str = Field(default="#3B82F6", pattern="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    isPublic: Optional[bool] = None
    logoUrl: Optional[str] = None
    themeColor: Optional[str] = Field(None, pattern="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$")

class ProjectResponse(ProjectBase):
    id: str
    ownerId: str
    createdAt: datetime
    deletedAt: Optional[datetime] = None # Importante para não dar erro de validação

    class Config:
        from_attributes = True

class ProjectMemberResponse(BaseModel):
    role: str
    userId: str
    user: UserSimple

    class Config:
        from_attributes = True

class ProjectFullResponse(ProjectResponse):
    owner: Optional[UserSimple] = None
    members: List[ProjectMemberResponse] = []

    class Config:
        from_attributes = True