from pydantic import BaseModel
from typing import Any, Optional, Dict
from datetime import datetime

class UserSimple(BaseModel):
    name: Optional[str]
    email: str

    class Config:
        from_attributes = True

class SubmissionBase(BaseModel):
    # Dict[str, Any] garante que o dado seja um JSON válido
    formData: Dict[str, Any] 

class SubmissionCreate(SubmissionBase):
    id: str        # UUID gerado no Mobile (Crucial para o RF 23)
    formId: str

class SubmissionUpdate(BaseModel):
    # Opcional para permitir atualizações parciais via PATCH
    formData: Optional[Dict[str, Any]] = None

class SubmissionResponse(SubmissionBase):
    id: str
    userId: str
    user: Optional[UserSimple] = None 
    formId: str
    createdAt: datetime

    class Config:
        from_attributes = True