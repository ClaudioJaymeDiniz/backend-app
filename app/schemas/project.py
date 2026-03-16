from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

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

    class Config:
        from_attributes = True