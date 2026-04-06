from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
# Importando do seu schema de user e submission (se o ProjectSimple estiver lá)
from app.schemas.user import UserSimple 

class InvitationStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REVOKED = "REVOKED"

class ProjectSimpleResponse(BaseModel):
    id: str
    name: str
    owner: Optional[UserSimple] = None

    class Config:
        from_attributes = True

class InvitationCreate(BaseModel):
    email: EmailStr
    projectId: str
    role: Optional[str] = "COLLECTOR"

class InvitationResponse(BaseModel):
    id: str
    email: str
    projectId: str
    status: InvitationStatus
    project: Optional[ProjectSimpleResponse] = None
    createdAt: datetime

    class Config:
        from_attributes = True