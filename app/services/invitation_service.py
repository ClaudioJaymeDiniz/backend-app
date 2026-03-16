from app.core.prisma_client import db
from fastapi import HTTPException
from app.core.mail import send_invitation_email

class InvitationService:
    @staticmethod
    async def invite_user(project_id: str, email: str, owner_id: str):
        # 1. Verificar se quem está convidando é o dono do projeto
        project = await db.project.find_unique(where={"id": project_id})
        if not project or project.ownerId != owner_id:
            raise HTTPException(status_code=403, detail="Apenas o dono pode convidar")

        # 2. Criar o convite no banco
        invitation = await db.project_invitation.create(
            data={
                "email": email,
                "projectId": project_id
            }
        )

        # 3. Disparar o e-mail (Atende ao RF 05)
        # Usamos await para garantir que o e-mail seja enviado antes de retornar sucesso
        try:
            await send_invitation_email(email, project.name)
        except Exception as e:
            # Opcional: Logar o erro, mas manter o convite criado no banco
            print(f"Erro ao enviar e-mail: {e}")

        return invitation

    @staticmethod
    async def check_access(project_id: str, user_email: str):
        """
        Verifica se um usuário tem permissão para ver/responder.
        Atende ao RF 17 (Autenticação para Respondentes Privados).
        """
        project = await db.project.find_unique(where={"id": project_id})
        
        # Se for público, qualquer um passa
        if project.isPublic:
            return True
            
        # Se for privado, checa se há um convite ou se ele já é membro
        invitation = await db.project_invitation.find_unique(
            where={"email_projectId": {"email": user_email, "projectId": project_id}}
        )
        
        #if invitation and invitation.status == "ACCEPTED":
            #return True
        if invitation and invitation.status in ["PENDING", "ACCEPTED"]:
            return True
            
        raise HTTPException(status_code=403, detail="Este projeto é privado e você não foi convidado.")