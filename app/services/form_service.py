import csv
import io
from app.core.prisma_client import db
from app.schemas.form import FormCreate, FormUpdate
from fastapi import HTTPException
#from fastapi.responses import StreamingResponse
from prisma import Json
from datetime import datetime

class FormService:
    
    @staticmethod
    async def create_form(data: FormCreate, user_id: str):
        # 1. Verificar projeto... (mantenha igual)
        project = await db.project.find_unique(where={"id": data.projectId})
        if not project or project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado ao projeto")
        
        # 2. Converter usando 'structure' que vem do Schema ajustado
        # Mudamos data.fields para data.structure
        fields_json = [field.model_dump() for field in data.structure]

        return await db.form.create(
            data={
                "title": data.title,
                "description": data.description,
                "structure": Json(fields_json), 
                "project": {
                    "connect": {"id": data.projectId}
                }
            }
        )

    @staticmethod
    async def get_forms_by_project(project_id: str):
        """Lista formulários ativos de um projeto."""
        return await db.form.find_many(
            where={
                "projectId": project_id,
                "deletedAt": None # Ignora formulários arquivados
            }
        )

    @staticmethod
    async def get_form_by_id(form_id: str):
        return await db.form.find_unique(where={"id": form_id})

    @staticmethod
    async def delete_form(form_id: str, user_id: str):
        form = await db.form.find_unique(
            where={"id": form_id},
            include={"project": True} # Pegamos o projeto para checar o dono
        )
        
        if not form or form.project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Apenas o dono do projeto pode excluir o formulário")

        return await db.form.delete(where={"id": form_id})
    

    @staticmethod
    async def get_all_submissions_for_form(form_id: str, user_id: str):
        # 1. Busca o formulário e traz junto os dados do projeto (include)
        form = await db.form.find_unique(
            where={"id": form_id},
            include={"project": True}
        )
        
        if not form:
            raise HTTPException(status_code=404, detail="Formulário não encontrado")

        # 2. Verifica se o usuário logado é o dono do projeto deste formulário
        if form.project.ownerId != user_id:
            raise HTTPException(
                status_code=403, 
                detail="Apenas o dono do projeto pode ver todas as respostas"
            )

        # 3. Retorna todas as submissões vinculadas a este formulário
        return await db.submission.find_many(
            where={"formId": form_id},
            include={"user": True}, # Inclui dados do aluno/coletor que respondeu
            order_by={"createdAt": "desc"}
        )
    
    @staticmethod
    async def archive_form(form_id: str, user_id: str):
        """
        Realiza a exclusão lógica (Soft Delete) do formulário.
        Valida se o usuário é o proprietário do projeto vinculado.
        """
        # 1. Busca otimizada: trazemos apenas o ownerId do projeto para validação
        form = await db.form.find_unique(
            where={"id": form_id},
            include={
                "project": {
                    "select": {"ownerId": True}
                }
            }
        )

        # 2. Guard Clause: Se não existe ou não é dono, barramos cedo
        if not form or form.project.ownerId != user_id:
            raise HTTPException(
                status_code=403, 
                detail="Acesso negado: você não tem permissão para arquivar este formulário"
            )

        # 3. Executa o update com o timestamp correto
        return await db.form.update(
            where={"id": form_id},
            data={"deletedAt": datetime.now()} # Agora chamando a função .now() corretamente
        )

    @staticmethod
    async def export_form_responses_csv(form_id: str, user_id: str):
        """
        Gera um arquivo CSV com todas as respostas do formulário.
        Atende ao RF 10 (Exportação de Respostas).
        """
        # 1. Busca o formulário e as submissões (validando o dono)
        form = await db.form.find_unique(
            where={"id": form_id},
            include={"project": True, "submissions": {"include": {"user": True}}}
        )
        
        if not form or form.project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        # 2. Prepara o "arquivo" na memória
        output = io.StringIO()
        writer = csv.writer(output)

        # 3. Define o Cabeçalho (Header)
        # Pegamos as labels da estrutura do formulário para serem os títulos das colunas
        header = ["Data de Envio", "Respondente (E-mail)"]
        field_labels = [field['label'] for field in form.structure]
        header.extend(field_labels)
        writer.writerow(header)

        # 4. Preenche as linhas com as respostas
        for sub in form.submissions:
            row = [
                sub.createdAt.strftime("%Y-%m-%d %H:%M:%S"),
                sub.user.email if sub.user else "Anônimo"
            ]
            # Busca o valor de cada campo no JSON formData
            for label in field_labels:
                # Se o campo não existir na resposta, fica vazio
                row.append(sub.formData.get(label, ""))
            writer.writerow(row)

        # 5. Retorna o fluxo de dados como um arquivo baixável
        output.seek(0)
        return output.getvalue()
    
    @staticmethod
    async def update_form(form_id: str, data: FormUpdate, user_id: str):
        # 1. Busca e validação... (mantenha igual)
        form = await db.form.find_unique(where={"id": form_id}, include={"project": True})
        if not form or form.project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        update_data = {}
        if data.title is not None: update_data["title"] = data.title
        if data.description is not None: update_data["description"] = data.description
        
        # 2. Ajuste aqui: data.fields vira data.structure
        if data.structure is not None:
            update_data["structure"] = Json([field.model_dump() for field in data.structure])

        return await db.form.update(
            where={"id": form_id},
            data=update_data
        )


    @staticmethod
    async def get_form_analytics(form_id: str, user_id: str):
        """
        Gera estatísticas básicas para o dashboard.
        Atende ao RF 11.
        """
        # 1. Verificar se o formulário existe e se o usuário é o dono
        form = await db.form.find_unique(
            where={"id": form_id},
            include={"project": True}
        )
        
        if not form or form.project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        # 2. Contar total de respostas
        total_responses = await db.submission.count(where={"formId": form_id})

        # 3. Agrupar respostas por data (Últimos 7 dias)
        # Nota: O Prisma permite fazer agrupamentos potentes
        submissions = await db.submission.find_many(
            where={"formId": form_id},
            select={"createdAt": True},
            order_by={"createdAt": "asc"}
        )

        # Pequena lógica para formatar os dados para o gráfico do Frontend
        daily_counts = {}
        for s in submissions:
            date_str = s["createdAt"].strftime("%d/%m")
            daily_counts[date_str] = daily_counts.get(date_str, 0) + 1

        return {
            "title": form.title,
            "total_responses": total_responses,
            "chart_data": [{"date": k, "count": v} for k, v in daily_counts.items()]
        }