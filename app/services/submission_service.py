from app.core.prisma_client import db
from fastapi import HTTPException
from app.schemas.submission import SubmissionUpdate
from app.core.mail import send_submission_notification



class SubmissionService:
    @staticmethod
    async def create_submission(data: dict, user_id: str):
        # 1. Salva a submissão no banco
        submission = await db.submission.create(
            data={
                "id": data["id"],
                "formData": data["formData"],
                "userId": user_id,
                "formId": data["formId"]
            }
        )

        # 2. Busca informações do dono para notificar (RF 15)
        # Fazemos isso em background para não atrasar a resposta do usuário
        form = await db.form.find_unique(
            where={"id": data["formId"]},
            include={
                "project": {
                    "include": {"owner": True}
                }
            }
        )

        if form and form.project.owner.email:
            try:
                await send_submission_notification(
                    owner_email=form.project.owner.email,
                    project_name=form.project.name,
                    form_title=form.title
                )
            except Exception as e:
                print(f"Erro ao enviar notificação: {e}")

        return submission

    @staticmethod
    async def update_submission(submission_id: str, data: SubmissionUpdate, user_id: str):
        submission = await db.submission.find_unique(where={"id": submission_id})
        
        if not submission:
            raise HTTPException(status_code=404, detail="Resposta não encontrada")
        
        # REGRA: Só o dono da submissão edita ela
        if submission.userId != user_id:
            raise HTTPException(status_code=403, detail="Você só pode editar suas próprias respostas")

        return await db.submission.update(
            where={"id": submission_id},
            data={"formData": data.formData}
        )

    @staticmethod
    async def get_my_submissions(user_id: str):
        return await db.submission.find_many(where={"userId": user_id})