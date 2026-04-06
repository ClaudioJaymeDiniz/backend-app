from app.core.prisma_client import db
from fastapi import HTTPException
from app.schemas.submission import SubmissionUpdate
from app.core.mail import send_submission_notification
from app.services.invitation_service import InvitationService
from prisma import Json
import traceback



class SubmissionService:
    @staticmethod
    async def create_submission(data: dict, user_id: str, user_email: str):
        # Valida os campos essenciais antes de persistir.
        submission_id = data.get("id")
        form_id = data.get("formId")
        form_data = data.get("formData")

        if not submission_id or not form_id or form_data is None:
            raise HTTPException(
                status_code=400,
                detail="Payload invalido. Campos obrigatorios: id, formId e formData."
            )

        try:
            # Verifica se o formulario existe e valida acesso para formulario privado.
            form_exists = await db.form.find_unique(where={"id": form_id})
            if not form_exists:
                raise HTTPException(status_code=404, detail="Formulario nao encontrado")

            if not form_exists.isPublic:
                await InvitationService.check_access(form_exists.projectId, user_id, user_email)

            submission = await db.submission.create(
                data={
                    "id": submission_id,
                    "formData": Json(form_data),
                    "user": {
                        "connect": {"id": user_id}
                    },
                    "form": {
                        "connect": {"id": form_id}
                    },
                }
            )

            # 2. Busca informações do dono para notificar (RF 15)
            # O include profundo permite acessar o email do owner através do projeto
            form_info = await db.form.find_unique(
                where={"id": form_id},
                include={
                    "project": {
                        "include": {
                            "owner": True
                        }
                    }
                }
            )

            # Disparo da notificação (Regra de Negócio: RF 15)
            if form_info and form_info.project.owner.email:
                try:
                    await send_submission_notification(
                        owner_email=form_info.project.owner.email,
                        project_name=form_info.project.name,
                        form_title=form_info.title
                    )
                except Exception as e:
                    # Logamos o erro de e-mail mas não travamos a resposta da API
                    print(f"⚠️ Erro ao enviar notificação (RF 15): {e}")

            return submission

        except HTTPException:
            raise

        except Exception as e:
            error_message = str(e)
            print(f"Erro critico ao criar submissao no Prisma: {error_message}")
            print(traceback.format_exc())

            # Mapeia erros comuns para status mais apropriados.
            if "Unique constraint failed" in error_message and "id" in error_message:
                raise HTTPException(status_code=409, detail="Submissao ja registrada")

            raise HTTPException(
                status_code=500, 
                detail="Erro interno ao processar a coleta de dados."
            )

    @staticmethod
    async def update_submission(submission_id: str, data: SubmissionUpdate, user_id: str):
        submission = await db.submission.find_unique(where={"id": submission_id})
        
        if not submission:
            raise HTTPException(status_code=404, detail="Resposta não encontrada")
        
        # REGRA: Só o dono da submissão edita ela
        if submission.userId != user_id:
            raise HTTPException(status_code=403, detail="Você só pode editar suas próprias respostas")

        if data.formData is None:
            raise HTTPException(status_code=400, detail="formData e obrigatorio para atualizacao")

        return await db.submission.update(
            where={"id": submission_id},
            data={"formData": Json(data.formData)}
        )

    @staticmethod
    async def get_my_submissions(user_id: str):
        return await db.submission.find_many(where={"userId": user_id})
    
    @staticmethod
    async def get_submissions_by_context(form_id: str, user_id: str):
        """
        Regra de Negócio:
        1. Busca o formulário e verifica quem é o dono do projeto.
        2. Se o user_id for o DONO do projeto, retorna TODAS as respostas.
        3. Se o user_id for apenas um participante, retorna apenas as DELE.
        """
        form = await db.form.find_unique(
            where={"id": form_id},
            include={"project": True}
        )

        if not form:
            raise HTTPException(status_code=404, detail="Formulário não encontrado")

        # Se for o dono do projeto (OWNER)
        if form.project.ownerId == user_id:
            return await db.submission.find_many(
                where={"formId": form_id},
                include={"user": True}, # Inclui dados de quem respondeu
                order={"createdAt": "desc"}
            )
        
        # Se for um coletor, filtra pelo ID dele
        return await db.submission.find_many(
            where={
                "formId": form_id,
                "userId": user_id
            },
            order={"createdAt": "desc"}
        )