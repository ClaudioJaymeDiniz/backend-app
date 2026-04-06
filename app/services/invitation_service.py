from app.core.prisma_client import db
from fastapi import HTTPException
from app.core.mail import send_invitation_email
from datetime import datetime

class InvitationService:
    @staticmethod
    # Alteramos os nomes para bater com o Schema: email e projectId
    async def create_invitation(projectId: str, email: str, owner_id: str, role: str = "COLLECTOR"):
        # 1. Validação: O projeto existe e quem está convidando é o dono?
        email_limpo = email.lower().strip()
        project = await db.project.find_unique(where={"id": projectId})
        if not project or project.ownerId != owner_id:
            raise HTTPException(status_code=403, detail="Acesso negado ao projeto")

        # 2. BUSCA DINÂMICA: O e-mail já é de alguém cadastrado no sistema?
        registered_user = await db.user.find_unique(where={"email": email})

        if registered_user:
    # Usuário ENCONTRADO: Vinculamos ao projeto
            await db.userproject.upsert(
                where={
                    "userId_projectId": {
                        "userId": registered_user.id,
                        "projectId": projectId
                    }
                },
                data={
                    "update": {
                        "role": role
                    },
                    "create": {
                        "userId": registered_user.id,
                        "projectId": projectId,
                        "role": role
                    }
                }
            )
            status = "ACCEPTED"
            u_id = registered_user.id
        else:
            # Usuário NÃO ENCONTRADO: Envia e-mail de convite para ele se cadastrar
            status = "PENDING"
            u_id = None
            try:
                await send_invitation_email(email, project.name)
            except Exception:
                print(f"Erro ao enviar e-mail para {email}, mas convite será criado.")

        # 3. Registra o histórico do convite
        return await db.projectinvitation.create(
            data={
                "email": email,
                "projectId": projectId,
                "status": status,
                "userId": u_id
            }
        )

    @staticmethod
    async def check_access(project_id: str, user_id: str, email: str):
        """Valida acesso por dono do projeto (id) ou convite aceito (email)."""
        project = await db.project.find_unique(where={"id": project_id})
        if not project:
            raise HTTPException(status_code=404, detail="Projeto nao encontrado")

        # Dono sempre tem acesso.
        if project.ownerId == user_id:
            return

        access = await db.projectinvitation.find_first(
            where={
                "projectId": project_id,
                "email": {
                    "equals": email,
                    "mode": "insensitive"
                },
                "status": "ACCEPTED"
            }
        )

        if not access:
            raise HTTPException(status_code=403, detail="Sem permissao de acesso")


    @staticmethod
    async def get_my_pending_invitations(email: str):
        """
        Busca todos os convites com status PENDING ignorando maiúsculas/minúsculas.
        """
        return await db.projectinvitation.find_many(
            where={
                "email": {
                    "equals": email,
                    "mode": "insensitive" # Isso resolve o problema de Claudio vs claudio
                },
                "status": "PENDING"
            },
            include={
                "project": {
                    "include": {
                        "owner": True 
                    }
                }
            },
            order={
                "createdAt": "desc"
            }
        )