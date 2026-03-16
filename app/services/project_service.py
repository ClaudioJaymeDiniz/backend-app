from datetime import datetime

from fastapi import HTTPException

from app.core.prisma_client import db
from app.schemas.project import ProjectCreate, ProjectUpdate

class ProjectService:
    @staticmethod
    async def create_project(data: ProjectCreate, owner_id: str):
        return await db.project.create(
            data={
                "name": data.name,
                "description": data.description,
                "isPublic": data.isPublic,
                "logoUrl": data.logoUrl,
                "themeColor": data.themeColor,
                "ownerId": owner_id
            }
        )
    '''
    @staticmethod
    async def get_projects_by_owner(owner_id: str):
        return await db.project.find_many(
            where={"ownerId": owner_id},
            include={"forms": True},
            order_by={"createdAt": "desc"} # Organiza do mais novo para o mais antigo
        )'''
    
    @staticmethod
    async def get_projects_by_owner(owner_id: str):
        """Retorna apenas projetos que NÃO foram arquivados."""
        return await db.project.find_many(
            where={
                "ownerId": owner_id,
                "deletedAt": None  # Filtro de exclusão lógica
            },
            include={"forms": True},
            order_by={"createdAt": "desc"}
        )

    @staticmethod
    async def get_project_by_id(project_id: str):
        return await db.project.find_unique(
            where={"id": project_id},
            include={"forms": True}
        )

    @staticmethod
    async def update_project(project_id: str, data: ProjectUpdate):
        # O exclude_unset=True é fundamental aqui para não resetar campos que não foram enviados
        update_data = data.model_dump(exclude_unset=True)
        return await db.project.update(
            where={"id": project_id},
            data=update_data
        )

    '''
    @staticmethod
    async def delete_project(project_id: str):
        return await db.project.delete(where={"id": project_id})
    '''
    
    @staticmethod
    async def archive_project(project_id: str):
        """
        Realiza a exclusão lógica (Soft Delete).
        Atende ao RF 14 (Exclusão Lógica).
        """
        return await db.project.update(
            where={"id": project_id},
            data={"deletedAt": datetime.now()}
        )
    
    @staticmethod
    async def restore_project(project_id: str, user_id: str):
        """Restaura um projeto removendo a data de exclusão."""
        # Verificamos se o projeto pertence ao usuário antes de restaurar
        project = await db.project.find_unique(where={"id": project_id})
        if not project or project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        return await db.project.update(
            where={"id": project_id},
            data={"deletedAt": None} # Define como nulo para "voltar à vida"
        )
    
    @staticmethod
    async def get_archived_projects(owner_id: str):
        """Lista apenas projetos que ESTÃO na lixeira (deletedAt não é nulo)."""
        return await db.project.find_many(
            where={
                "ownerId": owner_id,
                "NOT": {"deletedAt": None} # Filtra apenas os deletados
            },
            order_by={"deletedAt": "desc"}
        )