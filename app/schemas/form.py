
from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class FormField(BaseModel):
    fieldId: Optional[str] = None
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
    deletedAt: Optional[datetime] = None
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


class AnalyticsSeriesPoint(BaseModel):
    label: str
    count: int


class AnalyticsDailyPoint(BaseModel):
    date: str
    count: int


class AnalyticsFieldResponse(BaseModel):
    fieldId: str
    label: str
    type: str
    totalAnswered: int
    emptyCount: int
    chart: str
    series: List[AnalyticsSeriesPoint]
    stats: Optional[dict] = None


class FormAnalyticsResponse(BaseModel):
    formId: str
    title: str
    totalSubmissions: int
    completionRate: float
    dailySubmissions: List[AnalyticsDailyPoint]
    fields: List[AnalyticsFieldResponse]

