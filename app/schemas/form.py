
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class FormField(BaseModel):
    label: str
    type: str  # text, number, select, image, gps, etc.
    required: bool = True
    options: Optional[List[str]] = None  # Para campos tipo 'select'

class FormBase(BaseModel):
    title: str
    description: Optional[str] = None
    isPublic: bool = False

class FormCreate(FormBase):
    projectId: str
    structure: List[FormField]  # <--- Alterado de fields para structure

class FormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    isPublic: Optional[bool] = None
    structure: Optional[List[FormField]] = None

class FormResponse(FormBase):
    id: str
    projectId: str
    structure: Any  # O JSON que o Prisma retorna
    createdAt: datetime
    submissionCount: int = 0

    class Config:
        from_attributes = True

class FormPublicResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    isPublic: bool
    projectId: str
    projectName: str
    projectColor: Optional[str] = None
    ownerId: str

