from fastapi.responses import Response
from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.api.deps import get_current_user
from app.schemas.form import FormCreate, FormResponse
from app.services.form_service import FormService
from app.schemas.submission import SubmissionResponse
from app.services.invitation_service import InvitationService


router = APIRouter(prefix="/forms", tags=["Formulários"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=FormResponse)
async def create_form(data: FormCreate, user = Depends(get_current_user)):
    return await FormService.create_form(data, user.id)

@router.get("/project/{project_id}", response_model=List[FormResponse])
async def list_project_forms(project_id: str, user = Depends(get_current_user)):
    # Aqui poderíamos validar se o usuário tem acesso ao projeto antes de listar
    return await FormService.get_forms_by_project(project_id)

@router.get("/{form_id}", response_model=FormResponse)
async def get_form_details(form_id: str, user = Depends(get_current_user)):
    form = await FormService.get_form_by_id(form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Formulário não encontrado")
    return form

@router.get("/{form_id}/results", response_model=List[SubmissionResponse])
async def get_form_results(form_id: str, user = Depends(get_current_user)):
    """
    Retorna todas as respostas de um formulário. 
    Acesso restrito ao dono do projeto.
    """
    return await FormService.get_all_submissions_for_form(form_id, user.id)

@router.get("/{form_id}/export/csv")
async def export_responses(form_id: str, user = Depends(get_current_user)):
    """
    Gera e faz o download de um arquivo CSV com os dados coletados.
    """
    csv_data = await FormService.export_form_responses_csv(form_id, user.id)
    
    # Configuramos o cabeçalho de resposta para o navegador entender que é um download
    filename = f"respostas_form_{form_id[:8]}.csv"
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"'
    }
    
    return Response(content=csv_data, media_type="text/csv", headers=headers)

@router.get("/{form_id}", response_model=FormResponse)
async def get_form_details(form_id: str, user = Depends(get_current_user)):
    form = await FormService.get_form_by_id(form_id)
    if not form:
        raise HTTPException(status_code=404, detail="Formulário não encontrado")
    
    # Validação de acesso baseada no projeto (RF 04 e 17)
    await InvitationService.check_access(form.projectId, user.email)
    
    return form

@router.get("/{form_id}/analytics")
async def get_analytics(form_id: str, user = Depends(get_current_user)):
    return await FormService.get_form_analytics(form_id, user.id)