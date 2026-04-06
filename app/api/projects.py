from fastapi import APIRouter, Depends, status, HTTPException
from typing import List
from app.api.deps import get_current_user
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services.project_service import ProjectService
from app.core.prisma_client import db
from app.schemas.project import ProjectFullResponse


router = APIRouter(prefix="/projects", tags=["Projetos"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProjectResponse)
async def create_project(
    data: ProjectCreate, 
    user = Depends(get_current_user)
):
    return await ProjectService.create_project(data, user.id)

#@router.get("/", response_model=List[ProjectResponse])
#async def list_my_projects(user = Depends(get_current_user)):
    #return await ProjectService.get_projects_by_owner(user.id)

@router.get("/", response_model=List[ProjectResponse]) # Ou ProjectFullResponse se quiser os nomes
async def list_my_projects(user = Depends(get_current_user)):
    return await ProjectService.list_projects(user.id)

@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    data: ProjectUpdate,
    user = Depends(get_current_user)
):
    project = await ProjectService.get_project_by_id(project_id)
    if not project or project.ownerId != user.id:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    return await ProjectService.update_project(project_id, data)    

# Rota para ver a Lixeira
@router.get("/archived", response_model=List[ProjectResponse])
async def list_trash(user = Depends(get_current_user)):
    """Retorna a lista de projetos arquivados do usuário."""
    return await ProjectService.get_archived_projects(user.id)

# Rota para restaurar
@router.post("/{project_id}/restore", response_model=ProjectResponse)
async def restore(project_id: str, user = Depends(get_current_user)):
    """Tira o projeto da lixeira."""
    return await ProjectService.restore_project(project_id, user.id)

# Rota para deletar de vez (Hard Delete - opcional conforme RF 14)
@router.delete("/{project_id}/permanent")
async def permanent_delete(project_id: str, user = Depends(get_current_user)):
    """Exclui definitivamente do banco de dados."""
    project = await ProjectService.get_project_by_id(project_id)
    if not project or project.ownerId != user.id:
         raise HTTPException(status_code=404, detail="Projeto não encontrado")
    
    return await ProjectService.delete_project(project_id)

@router.get("/{project_id}", response_model=ProjectFullResponse)
async def get_project(project_id: str, current_user = Depends(get_current_user)):
    project = await db.project.find_unique(
        where={"id": project_id},
        include={
            "owner": True,
            "members": {
                "include": {
                    "user": True
                }
            }
        }
    )
    
    if not project:
        raise HTTPException(status_code=404, detail="Projeto não encontrado")
        
    return project