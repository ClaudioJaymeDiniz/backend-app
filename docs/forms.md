📑 Referência de API: Módulo de Formulários (Form)

O módulo de formulários gerencia a estrutura dinâmica das coletas de dados e o processamento dos resultados para os usuários.
🗄️ Modelo de Dados (Prisma Entity)

O formulário armazena a "receita" de como o App Mobile deve renderizar os campos.
Campo	Tipo	Descrição
id	String (UUID)	Identificador único.
title	String	Nome do formulário (ex: "Censo escolar").
structure	Json	Array de objetos contendo label, type e required.
projectId	String	FK para o projeto pai.
createdAt	DateTime	Data de criação.
deletedAt	DateTime?	Controle de exclusão lógica (arquivamento).
🛠️ Service: FormService

Este serviço contém a lógica pesada de transformação de dados e exportação.

    create_form: Valida a propriedade do projeto e converte a lista de objetos Pydantic em um formato JSON puro que o PostgreSQL/Prisma consegue armazenar.

    export_form_responses_csv: Executa o RF 10. Ele varre todas as submissões, extrai as chaves do JSON de resposta e monta um arquivo CSV em memória usando io.StringIO, evitando o uso de disco no servidor Linux.

    get_form_analytics: Implementa o RF 11. Realiza agregações temporais para alimentar gráficos de "Respostas por Dia".

    update_form: Permite a evolução do formulário (RF 13), atualizando o título ou mudando a estrutura de campos dinamicamente.

🚀 Rotas e Endpoints (/forms)
1. Criar Formulário

    Rota: POST /forms/

    Entrada: FormCreate (Inclui lista de fields).

    Regra: Só pode ser criado se o user_id for o dono do projectId.

2. Listar Formulários do Projeto

    Rota: GET /forms/project/{project_id}

    Descrição: Retorna todos os formulários ativos vinculados a um projeto específico.

3. Resultados e Analytics

    Rota: GET /forms/{form_id}/results

        Descrição: Lista todas as respostas individuais (Submissions) com dados do respondente.

    Rota: GET /forms/{form_id}/analytics

        Descrição: Retorna dados sumarizados (Total e contagem diária) para dashboards.

4. Exportação (Download)

    Rota: GET /forms/{form_id}/export/csv

    Descrição: Retorna um fluxo de dados (Stream) que o navegador/celular interpreta como um download de arquivo .csv.

    Headers: Content-Disposition configurado para sugerir o nome do arquivo dinamicamente.

    🔐 Schemas de Estrutura Dinâmica
Classe	Descrição
FormField	Define um campo individual: label, type (text, number, image, etc), e se é required.
FormCreate	Recebe o projectId e a lista de FormField.
FormResponse	Retorna o objeto completo. O campo structure é devolvido como Any (JSON nativo).
