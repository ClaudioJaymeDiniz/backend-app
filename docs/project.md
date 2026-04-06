📑 Documentação de API: Módulo de Projetos (Project)

Este módulo gerencia o agrupamento de formulários e membros, permitindo a personalização visual (cores e logos) e o controle de privacidade.
🗄️ Modelo de Dados (Prisma Entity)

O projeto atua como o container principal para as coletas de dados.
Campo	Tipo	Descrição
id	String (UUID)	Identificador único do projeto.
name	String	Nome visível do projeto.
description	String?	Detalhes sobre o objetivo do projeto.
themeColor	String	Cor hexadecimal para a identidade visual no App.
ownerId	String	FK para o usuário criador (proprietário).
isPublic	Boolean	Define se o projeto aceita coletas públicas.
deletedAt	DateTime?	Data de arquivamento. Se preenchido, o projeto está na "Lixeira".
🛠️ Service: ProjectService

Camada de lógica que gerencia o estado dos projetos.

    create_project: Instancia um novo projeto vinculado ao owner_id logado.

    get_projects_by_owner: Filtra projetos ativos (deletedAt == None). Note o uso do include={"forms": True} para carregar os formulários vinculados em uma única consulta (Eager Loading).

    archive_project: Transforma uma exclusão em arquivamento (Soft Delete), preenchendo o campo deletedAt.

    restore_project: Reverte o arquivamento, limpando o campo deletedAt.

    delete_project: Executa o Hard Delete (exclusão permanente), removendo o registro fisicamente do PostgreSQL.

🚀 Rotas e Endpoints (FastAPI)
1. Criar Projeto

POST /projects/

    Body (Schema: ProjectCreate):
    {
  "name": "Pesquisa de Campo FATEC",
  "description": "Coleta de dados sobre sustentabilidade",
  "themeColor": "#059669"
}

2. Listar Projetos Ativos

GET /projects/

    Descrição: Retorna apenas os projetos que não foram arquivados. Útil para a tela inicial do App.

3. Gestão da Lixeira (Soft Delete)

    GET /projects/archived: Lista projetos deletados logicamente.

    POST /projects/{project_id}/restore: Restaura um projeto da lixeira.

    DELETE /projects/{project_id}/permanent: Exclui definitivamente (apenas o dono pode realizar esta ação).

🔐 Regras de Validação e Segurança
Validação de Cores (Regex)

No seu ProjectUpdate e ProjectBase, usamos o Field do Pydantic com padrão Regex:
pattern="^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
Isso garante que o banco de dados nunca receba uma cor inválida que poderia quebrar o layout do React Native.
Proteção de Escopo

Todas as rotas verificam se o ownerId do projeto corresponde ao id do usuário vindo do token JWT. Se um usuário tentar acessar o ID de um projeto que não lhe pertence, o sistema retorna 404 Not Found (por segurança, para não confirmar a existência do ID) ou 403 Forbidden.

📑 Referência de API: Endpoints de Projetos (/projects)

Todos os endpoints abaixo exigem o cabeçalho Authorization: Bearer <token>.
1. Criar Novo Projeto

    Rota: POST /projects/

    Função: create_project

    Entrada: Objeto ProjectCreate.

    Regra: O ownerId é preenchido automaticamente com o ID do usuário logado.

    Sucesso (201): Retorna o projeto criado com seu novo id (UUID).

2. Listar Meus Projetos (Ativos)

    Rota: GET /projects/

    Função: list_my_projects

    Descrição: Retorna uma lista de projetos onde o usuário é o dono e deletedAt é nulo.

    Diferencial: Inclui a lista de formulários (forms) dentro de cada projeto graças ao include no Service.

3. Obter Detalhes de um Projeto

    Rota: GET /projects/{project_id}

    Função: get_project

    Validações: 1. O projeto deve existir.
    2. O usuário logado deve ser o dono (ownerId).
    3. O projeto não pode estar arquivado (deletedAt deve ser None).

    Erro (404): Retornado se qualquer uma das condições acima falhar (por segurança, não diferenciamos "inexistente" de "sem permissão").

4. Atualizar Projeto

    Rota: PATCH /projects/{project_id}

    Função: update_project

    Entrada: ProjectUpdate (Todos os campos são opcionais).

    Comportamento: O uso de exclude_unset=True permite atualizar apenas a cor (themeColor) sem apagar o nome, por exemplo.

5. Listar Arquivados (Lixeira)

    Rota: GET /projects/archived

    Função: list_trash

    Descrição: Retorna os projetos que sofreram "Soft Delete". Essencial para a funcionalidade de recuperação de dados do usuário (RF 14).

6. Restaurar Projeto

    Rota: POST /projects/{project_id}/restore

    Função: restore

    Ação: Define o campo deletedAt de volta para null. O projeto volta a aparecer na listagem principal (GET /projects/).

7. Exclusão Permanente (Hard Delete)

    Rota: DELETE /projects/{project_id}/permanent

    Função: permanent_delete

    Ação: Remove o registro e todas as suas dependências (se configurado no Prisma) definitivamente do PostgreSQL. Esta ação não pode ser desfeita.

    Método,Endpoint,Schema Entrada,Descrição Técnica
POST,/,ProjectCreate,Persistência inicial no DB.
GET,/,-,Query filtrada por ownerId e deletedAt IS NULL.
GET,/{id},-,Fetch único com validação de escopo de usuário.
PATCH,/{id},ProjectUpdate,Atualização atômica de campos via model_dump.
GET,/archived,-,Query filtrada por ownerId e deletedAt IS NOT NULL.
POST,/{id}/restore,-,Update no campo de timestamp para nulo.
DELETE,/{id}/permanent,-,Execução de db.project.delete().