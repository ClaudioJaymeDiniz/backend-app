import csv
import io
from app.core.prisma_client import db
from app.schemas.form import FormCreate, FormUpdate
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

class FormService:
    @staticmethod
    async def create_form(data: FormCreate, user_id: str):
        # Verificar se o projeto existe e pertence ao usuário
        project = await db.project.find_unique(where={"id": data.projectId})
        
        if not project or project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado ao projeto")

        # Mapeamos 'fields' do Pydantic para 'structure' do Prisma
        fields_json = [field.model_dump() for field in data.fields]

        return await db.form.create(
            data={
                "title": data.title,
                "description": data.description,
                "projectId": data.projectId,
                "structure": fields_json
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
        """Arquiva um formulário específico."""
        from datetime import datetime
        # Verificação de dono antes de arquivar
        form = await db.form.find_unique(
            where={"id": form_id},
            include={"project": True}
        )
        if not form or form.project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        return await db.form.update(
            where={"id": form_id},
            data={"deletedAt": datetime()}
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
        """
        Atualiza a estrutura do formulário de forma segura.
        Atende ao RF 13 (Edição).
        """
        # 1. Busca o formulário para validar permissão
        form = await db.form.find_unique(
            where={"id": form_id},
            include={"project": True}
        )

        if not form:
            raise HTTPException(status_code=404, detail="Formulário não encontrado")
        
        if form.project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        # 2. Prepara o dicionário de atualização (apenas o que foi enviado)
        update_data = {}
        if data.title is not None: 
            update_data["title"] = data.title
        if data.description is not None: 
            update_data["description"] = data.description
        if data.fields is not None:
            # Converte a lista de objetos Pydantic em JSON para o Prisma
            update_data["structure"] = [field.model_dump() for field in data.fields]

        # 3. Executa a atualização
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