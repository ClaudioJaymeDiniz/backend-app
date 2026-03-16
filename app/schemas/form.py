
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

class FormCreate(FormBase):
    projectId: str
    fields: List[FormField]

class FormResponse(FormBase):
    id: str
    projectId: str
    structure: Any  # O JSON que o Prisma retorna
    createdAt: datetime

    class Config:
        from_attributes = True

class FormUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[FormField]] = None