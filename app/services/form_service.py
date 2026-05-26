import csv
import io
import re
import unicodedata
from app.core.prisma_client import db
from app.schemas.form import FormCreate, FormUpdate
from fastapi import HTTPException
#from fastapi.responses import StreamingResponse
from prisma import Json
from datetime import datetime
from collections import Counter


def _slugify(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", ascii_text).strip("_").lower()
    return slug or "field"


def _normalize_form_structure(structure: list) -> list:
    """Garante que cada campo tenha fieldId estável e único dentro do formulário."""
    used_ids = set()
    normalized = []

    for index, raw_field in enumerate(structure or []):
        field = dict(raw_field)
        provided_field_id = field.get("fieldId")
        base_id = _slugify(provided_field_id or field.get("label") or f"field_{index + 1}")

        field_id = base_id
        suffix = 2
        while field_id in used_ids:
            field_id = f"{base_id}_{suffix}"
            suffix += 1

        used_ids.add(field_id)
        field["fieldId"] = field_id
        normalized.append(field)

    return normalized


def _structure_changed(original: list, normalized: list) -> bool:
    if len(original or []) != len(normalized or []):
        return True

    for index, field in enumerate(normalized or []):
        if (original[index] or {}).get("fieldId") != field.get("fieldId"):
            return True

    return False


def _field_value_from_submission(submission_data: dict, field: dict):
    """Suporta payload legado (label) e novo payload (fieldId)."""
    field_id = field.get("fieldId")
    label = field.get("label")

    if field_id and field_id in submission_data:
        return submission_data.get(field_id)

    if label and label in submission_data:
        return submission_data.get(label)

    return None


def _is_empty_value(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return len(value.strip()) == 0
    if isinstance(value, list):
        return len(value) == 0
    return False


def _build_field_analytics(field: dict, submissions: list) -> dict:
    field_id = field.get("fieldId")
    label = field.get("label", field_id)
    field_type = (field.get("type") or "text").lower()

    values = []
    total_answered = 0
    for submission in submissions:
        value = _field_value_from_submission(submission.formData or {}, field)
        values.append(value)
        if not _is_empty_value(value):
            total_answered += 1

    total_submissions = len(submissions)
    empty_count = max(total_submissions - total_answered, 0)

    # Select e checkbox geram distribuição por opção.
    if field_type in {"select", "checkbox"}:
        counter = Counter()
        for value in values:
            if _is_empty_value(value):
                continue
            if isinstance(value, list):
                for item in value:
                    counter[str(item)] += 1
            else:
                counter[str(value)] += 1

        options = field.get("options") or []
        option_counts = [{"label": option, "count": counter.get(option, 0)} for option in options]
        extras = [{"label": key, "count": count} for key, count in counter.items() if key not in set(options)]

        return {
            "fieldId": field_id,
            "label": label,
            "type": field_type,
            "totalAnswered": total_answered,
            "emptyCount": empty_count,
            "chart": "pie" if field_type == "select" else "bar",
            "series": option_counts + extras,
            "stats": None,
        }

    # Campos numéricos retornam estatísticas + histograma simples por valor.
    if field_type == "number":
        numeric_values = []
        for value in values:
            if _is_empty_value(value):
                continue
            try:
                numeric_values.append(float(value))
            except (TypeError, ValueError):
                continue

        number_counter = Counter(str(v).rstrip("0").rstrip(".") if isinstance(v, float) else str(v) for v in numeric_values)
        stats = None
        if numeric_values:
            sorted_values = sorted(numeric_values)
            midpoint = len(sorted_values) // 2
            if len(sorted_values) % 2 == 0:
                median = (sorted_values[midpoint - 1] + sorted_values[midpoint]) / 2
            else:
                median = sorted_values[midpoint]

            stats = {
                "min": min(numeric_values),
                "max": max(numeric_values),
                "avg": round(sum(numeric_values) / len(numeric_values), 2),
                "median": median,
            }

        return {
            "fieldId": field_id,
            "label": label,
            "type": field_type,
            "totalAnswered": total_answered,
            "emptyCount": empty_count,
            "chart": "bar",
            "series": [{"label": k, "count": c} for k, c in number_counter.most_common(20)],
            "stats": stats,
        }

    # Datas retornam série temporal por dia.
    if field_type == "date":
        date_counter = Counter()
        for value in values:
            if _is_empty_value(value):
                continue
            date_counter[str(value)] += 1

        ordered_series = [{"label": k, "count": date_counter[k]} for k in sorted(date_counter.keys())]
        return {
            "fieldId": field_id,
            "label": label,
            "type": field_type,
            "totalAnswered": total_answered,
            "emptyCount": empty_count,
            "chart": "line",
            "series": ordered_series,
            "stats": None,
        }

    # Campos de mídia mostram cobertura de envio.
    if field_type in {"image", "file"}:
        with_attachment = total_answered
        without_attachment = empty_count
        return {
            "fieldId": field_id,
            "label": label,
            "type": field_type,
            "totalAnswered": total_answered,
            "emptyCount": empty_count,
            "chart": "bar",
            "series": [
                {"label": "Com anexo", "count": with_attachment},
                {"label": "Sem anexo", "count": without_attachment},
            ],
            "stats": None,
        }

    # Text/textarea e tipos desconhecidos: top valores + métricas básicas.
    text_counter = Counter()
    lengths = []
    for value in values:
        if _is_empty_value(value):
            continue
        value_text = str(value).strip()
        text_counter[value_text] += 1
        lengths.append(len(value_text))

    stats = None
    if lengths:
        stats = {
            "avgLength": round(sum(lengths) / len(lengths), 2),
            "maxLength": max(lengths),
        }

    return {
        "fieldId": field_id,
        "label": label,
        "type": field_type,
        "totalAnswered": total_answered,
        "emptyCount": empty_count,
        "chart": "bar",
        "series": [{"label": k, "count": c} for k, c in text_counter.most_common(10)],
        "stats": stats,
    }

class FormService:
    
    @staticmethod
    async def create_form(data: FormCreate, user_id: str):
        # 1. Verificar projeto... (mantenha igual)
        project = await db.project.find_unique(where={"id": data.projectId})
        if not project or project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado ao projeto")
        
        # 2. Converter usando 'structure' que vem do Schema ajustado
        # Mudamos data.fields para data.structure
        fields_json = _normalize_form_structure([field.model_dump() for field in data.structure])

        return await db.form.create(
            data={
                "title": data.title,
                "description": data.description,
                "isPublic": data.isPublic,
                "structure": Json(fields_json), 
                "project": {
                    "connect": {"id": data.projectId}
                }
            }
        )

    @staticmethod
    async def get_forms_by_project(project_id: str):
        """Lista formulários ativos de um projeto com contagem de submissões."""
        forms = await db.form.find_many(
            where={
                "projectId": project_id,
                "deletedAt": None # Ignora formulários arquivados
            },
            include={"submissions": True}
        )
        
        # Adiciona o submissionCount ao response contando as submissões
        response = []
        for f in forms:
            normalized_structure = _normalize_form_structure(f.structure or [])
            if _structure_changed(f.structure or [], normalized_structure):
                await db.form.update(
                    where={"id": f.id},
                    data={"structure": Json(normalized_structure)}
                )

            response.append(
                {
                    "id": f.id,
                    "title": f.title,
                    "description": f.description,
                    "isPublic": f.isPublic,
                    "structure": normalized_structure,
                    "projectId": f.projectId,
                    "createdAt": f.createdAt,
                    "deletedAt": f.deletedAt,
                    "submissionCount": len(f.submissions)
                }
            )

        return response

    @staticmethod
    async def get_public_forms(user_id: str = None):
        forms = await db.form.find_many(
            where={
                "isPublic": True,
                "deletedAt": None
            },
            include={"project": True},
            order={"createdAt": "desc"}
        )

        active_project_forms = [
            f for f in forms
            if f.project and f.project.deletedAt is None
        ]

        return [
            {
                "id": f.id,
                "title": f.title,
                "description": f.description,
                "isPublic": f.isPublic,
                "projectId": f.projectId,
                "projectName": f.project.name,
                "projectColor": f.project.themeColor,
                "ownerId": f.project.ownerId,  # Adicionamos o ID do dono para filtrar no frontend
            }
            for f in active_project_forms
        ]

    @staticmethod
    async def get_form_by_id(form_id: str):
        form = await db.form.find_unique(
            where={"id": form_id},
            include={"project": True}
        )

        if form and form.project and form.project.deletedAt is not None:
            raise HTTPException(status_code=400, detail="Projeto arquivado")

        if form:
            normalized_structure = _normalize_form_structure(form.structure or [])
            if _structure_changed(form.structure or [], normalized_structure):
                form = await db.form.update(
                    where={"id": form.id},
                    data={"structure": Json(normalized_structure)},
                    include={"project": True}
                )

        return form

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
            include={"project": True}
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
            data={"deletedAt": datetime.now()}
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
        header = ["Data de Envio", "E-mail"]
        normalized_structure = _normalize_form_structure(form.structure or [])
        field_labels = [field.get("label", field.get("fieldId", "Campo")) for field in normalized_structure]
        header.extend(field_labels)
        writer.writerow(header)

        # 4. Preenche as linhas com as respostas
        for sub in form.submissions:
            row = [
                sub.createdAt.strftime("%Y-%m-%d %H:%M:%S"),
                sub.user.email if sub.user else "Anônimo"
            ]
            # Busca o valor de cada campo no JSON formData
            for field in normalized_structure:
                value = _field_value_from_submission(sub.formData or {}, field)
                row.append("" if value is None else value)
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
        if data.isPublic is not None: update_data["isPublic"] = data.isPublic
        
        # 2. Ajuste aqui: data.fields vira data.structure
        if data.structure is not None:
            update_data["structure"] = Json(_normalize_form_structure([field.model_dump() for field in data.structure]))

        return await db.form.update(
            where={"id": form_id},
            data=update_data
        )


    @staticmethod
    async def get_form_analytics(form_id: str, user_id: str):
        """
        Retorna analytics dinâmico por campo, compatível com formulários de estrutura variável.
        """
        form = await db.form.find_unique(
            where={"id": form_id},
            include={"project": True}
        )
        
        if not form or form.project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        submissions = await db.submission.find_many(
            where={"formId": form_id},
            order_by={"createdAt": "asc"}
        )

        structure = _normalize_form_structure(form.structure or [])
        if _structure_changed(form.structure or [], structure):
            await db.form.update(
                where={"id": form.id},
                data={"structure": Json(structure)}
            )

        daily_counts = Counter()
        for s in submissions:
            date_str = s.createdAt.strftime("%Y-%m-%d")
            daily_counts[date_str] += 1

        daily_series = [{"date": day, "count": daily_counts[day]} for day in sorted(daily_counts.keys())]

        fields_analytics = [_build_field_analytics(field, submissions) for field in structure]

        total_possible_answers = len(submissions) * len(structure)
        total_answered = sum(field_data["totalAnswered"] for field_data in fields_analytics)
        completion_rate = round(total_answered / total_possible_answers, 4) if total_possible_answers else 0.0

        return {
            "formId": form.id,
            "title": form.title,
            "totalSubmissions": len(submissions),
            "completionRate": completion_rate,
            "dailySubmissions": daily_series,
            "fields": fields_analytics,
        }
    
    @staticmethod
    async def restore_form(form_id: str, user_id: str):
        """Recuperação da Lixeira"""
        # Mesma validação de dono
        form = await db.form.find_unique(
            where={"id": form_id},
            include={"project": True}
        )
        
        if not form or form.project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Sem permissão para restaurar")

        return await db.form.update(
            where={"id": form_id},
            data={"deletedAt": None}
        )

    @staticmethod
    async def delete_form_permanent(form_id: str, user_id: str):
        """Hard Delete (Deletar de vez)"""
        form = await db.form.find_unique(
            where={"id": form_id},
            include={"project": True}
        )
        
        if not form:
            return {"ok": True, "alreadyDeleted": True}

        if form.project.ownerId != user_id:
            raise HTTPException(status_code=403, detail="Acesso negado")

        if form.deletedAt is None:
            raise HTTPException(status_code=400, detail="O formulário precisa ser arquivado antes de ser excluído definitivamente")

        await db.submission.delete_many(where={"formId": form_id})

        return await db.form.delete(where={"id": form_id})