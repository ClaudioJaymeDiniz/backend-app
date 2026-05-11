from datetime import datetime
from fastapi import HTTPException
from app.core.prisma_client import db
from app.schemas.project import ProjectCreate, ProjectUpdate
import traceback

class ProjectService:
    @staticmethod
    async def create_project(data: ProjectCreate, user_id: str):
        return await db.project.create(
            data={
                "name": data.name,
                "description": data.description,
                "themeColor": data.themeColor,
                "ownerId": user_id,
                "members": {
                    "create": {
                        "userId": user_id,
                        "role": "OWNER"
                    }
                }
            }
        )
    
    @staticmethod
    async def get_projects_by_owner(owner_id: str):
        """Retorna apenas projetos que NÃO foram arquivados."""
        return await db.project.find_many(
            where={
                "ownerId": owner_id,
                "deletedAt": None  # Filtro de exclusão lógica
            },
            include={"forms": True},
            order={"createdAt": "desc"} # CORREÇÃO: 'order' em vez de 'order_by'
        )

    @staticmethod
    async def get_project_by_id(project_id: str):
        return await db.project.find_unique(
            where={"id": project_id},
            include={
                "owner": True,      # Traz os dados do dono
                "members": {        # Traz a lista da tabela UserProject
                    "include": {
                        "user": True # Traz o nome/email do membro de dentro de UserProject
                    }
                }
            }
        )

    @staticmethod
    async def update_project(project_id: str, data: ProjectUpdate):
        update_data = data.model_dump(exclude_unset=True)
        return await db.project.update(
            where={"id": project_id},
            data=update_data
        )

    @staticmethod
    async def archive_project(project_id: str, user_id: str):
        """Realiza a exclusão lógica (Soft Delete)."""
        project = await db.project.find_unique(where={"id": project_id})
        if not project or project.ownerId != user_id:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")

        return await db.project.update(
            where={"id": project_id},
            data={"deletedAt": datetime.now()}
        )
    
    @staticmethod
    async def restore_project(project_id: str, user_id: str):
        project = await db.project.find_unique(where={"id": project_id})
        if not project or project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        return await db.project.update(
            where={"id": project_id},
            data={"deletedAt": None}
        )
    
    @staticmethod
    async def get_archived_projects(owner_id: str):
        """Lista apenas projetos que ESTÃO na lixeira."""
        return await db.project.find_many(
            where={
                "ownerId": owner_id,
                "NOT": {"deletedAt": None}
            },
            order={"deletedAt": "desc"} # CORREÇÃO: 'order' em vez de 'order_by'
        )

    @staticmethod
    async def delete_project(project_id: str):
        """Exclusão permanente do banco."""
        project = await db.project.find_unique(where={"id": project_id})
        if not project:
            # Idempotente: se ja foi deletado, consideramos sucesso.
            return {"ok": True, "alreadyDeleted": True}

        if project.deletedAt is None:
            raise HTTPException(status_code=400, detail="O projeto precisa ser arquivado antes de ser excluído definitivamente")

        try:
            forms = await db.form.find_many(where={"projectId": project_id})

            for form in forms:
                await db.submission.delete_many(where={"formId": form.id})

            await db.form.delete_many(where={"projectId": project_id})
            await db.projectinvitation.delete_many(where={"projectId": project_id})
            await db.userproject.delete_many(where={"projectId": project_id})

            return await db.project.delete(where={"id": project_id})
        except Exception as e:
            print(f"Erro ao excluir projeto definitivamente ({project_id}): {e}")
            print(traceback.format_exc())
            raise HTTPException(
                status_code=500,
                detail="Nao foi possivel excluir definitivamente o projeto"
            )

    @staticmethod
    async def delete_project_permanent_as_owner(project_id: str, user_id: str):
        """
        Exclui definitivamente de forma idempotente para o dono.
        Se o projeto ja nao existir, retorna sucesso para evitar loop no sync.
        """
        project = await db.project.find_unique(where={"id": project_id})

        if not project:
            return {"ok": True, "alreadyDeleted": True}

        if project.ownerId != user_id:
            raise HTTPException(status_code=404, detail="Projeto não encontrado")

        return await ProjectService.delete_project(project_id)

    @staticmethod
    async def list_projects(user_id: str):
        """
        Retorna projetos onde o usuário é o dono OU é um membro convidado.
        """
        return await db.project.find_many(
            where={
                "deletedAt": None, # Apenas projetos ativos
                "OR": [
                    {"ownerId": user_id}, # Projetos que eu criei
                    {
                        "members": {
                            "some": {"userId": user_id} # Projetos onde sou membro
                        }
                    }
                ]
            },
            include={
                "owner": True,
                "forms": True
            },
            order={"createdAt": "desc"}
        )