from app.core.prisma_client import db
from fastapi import HTTPException
from app.schemas.submission import SubmissionUpdate
from app.core.mail import send_submission_notification



class SubmissionService:
    @staticmethod
    async def create_submission(data: dict, user_id: str):
        # 1. Salva a submissão no banco usando a sintaxe de conexão do Prisma
        try:
            submission = await db.submission.create(
                data={
                    "id": data["id"],
                    # Garante que o formData seja tratado como JSON/Dict
                    "formData": data["formData"],
                    # Uso do 'connect' para garantir integridade referencial com User
                    "user": {
                        "connect": {"id": user_id}
                    },
                    # Uso do 'connect' para garantir integridade referencial com Form
                    "form": {
                        "connect": {"id": data["formId"]}
                    }
                }
            )

            # 2. Busca informações do dono para notificar (RF 15)
            # O include profundo permite acessar o email do owner através do projeto
            form_info = await db.form.find_unique(
                where={"id": data["formId"]},
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

        except Exception as e:
            # Log detalhado no console do Linux Mint para debug
            print(f"❌ Erro crítico ao criar submissão no Prisma: {e}")
            # Retorna 500 para o mobile saber que deve manter na fila de sync (SQLite)
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

        return await db.submission.update(
            where={"id": submission_id},
            data={"formData": data.formData}
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