from fastapi import APIRouter, Depends, status
from typing import List
from app.api.deps import get_current_user
from app.schemas.submission import SubmissionCreate, SubmissionResponse, SubmissionUpdate
from app.services.submission_service import SubmissionService

router = APIRouter(prefix="/submissions", tags=["Submissões (Respostas)"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=SubmissionResponse)
async def submit_form(data: SubmissionCreate, user = Depends(get_current_user)):
    # Convertemos o Pydantic para dict para facilitar o uso no Service
    # e garantimos que o userId logado seja o dono da submissão
    submission_data = data.model_dump()
    return await SubmissionService.create_submission(submission_data, user.id, user.email)

@router.patch("/{submission_id}", response_model=SubmissionResponse)
async def update_my_submission(
    submission_id: str, 
    data: SubmissionUpdate, 
    user = Depends(get_current_user)
):
    return await SubmissionService.update_submission(submission_id, data, user.id)

@router.get("/me", response_model=List[SubmissionResponse])
async def list_my_responses(user = Depends(get_current_user)):
    return await SubmissionService.get_my_submissions(user.id)

@router.get("/form/{form_id}", response_model=List[SubmissionResponse])
async def list_form_submissions(
    form_id: str, 
    user = Depends(get_current_user)
):
    """
    Retorna as respostas de um formulário específico.
    A lógica de quem vê o quê está isolada no Service.
    """
    return await SubmissionService.get_submissions_by_context(form_id, user.id)