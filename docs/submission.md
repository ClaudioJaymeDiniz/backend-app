📑 Referência de API: Módulo de Submissões (Submission)

Este módulo gerencia o armazenamento, a integridade e o controle de visibilidade das respostas enviadas pelos coletores em campo.
🗄️ Modelo de Dados (Prisma Entity)

A submissão é o registro final da coleta de dados.
Campo	Tipo	Descrição
id	String	Chave primária. Gerada pelo Mobile (UUID) para garantir unicidade no Sync Offline.
formData	Json	Objeto contendo o par pergunta: resposta.
userId	String	FK para o usuário que realizou a coleta.
formId	String	FK para o formulário respondido.
createdAt	DateTime	Data e hora exata do recebimento no servidor.
🛠️ Service: SubmissionService

Responsável pelo processamento de dados e regras de visibilidade.

    create_submission:

        Persiste a resposta no banco.

        Implementação do RF 15: Realiza uma busca profunda (deep include) para encontrar o e-mail do dono do projeto e disparar uma notificação via send_submission_notification.

    update_submission:

        Valida se o user_id da requisição é o mesmo que criou a submissão.

        Impede que um coletor altere a resposta de outro.

    get_submissions_by_context:

        Lógica de Privilégio:

            Se o usuário é Proprietário (Owner) do projeto, a query retorna o conjunto total de respostas do formulário.

            Se o usuário é Coletor (Collector), a query é filtrada para retornar apenas as respostas vinculadas ao seu próprio userId.

🚀 Rotas e Endpoints (/submissions)
1. Enviar Resposta

    Rota: POST /submissions/

    Schema de Entrada: SubmissionCreate

    Importância Técnica: Diferente de outros modelos, o id é enviado pelo cliente. Isso permite que o App Mobile gere o ID mesmo sem internet; ao recuperar a conexão, o backend aceita esse ID, evitando duplicidade em caso de reenvios.

2. Listar Minhas Respostas

    Rota: GET /submissions/me

    Descrição: Retorna o histórico pessoal do coletor logado em todos os projetos.

3. Consultar Respostas de um Formulário

    Rota: GET /submissions/form/{form_id}

    Comportamento Dinâmico: Esta rota muda o resultado baseado no cargo (Role) do usuário. É o endpoint principal para alimentar as listas de resultados no App.

4. Editar Resposta Existente

    Rota: PATCH /submissions/{submission_id}

    Uso: Permite correções em dados enviados, desde que o usuário possua a propriedade do registro.

🔐 Schemas de Validação (Pydantic)
Classe	Detalhe
SubmissionCreate	Exige id (string), formId e formData (dicionário).
SubmissionResponse	Inclui o objeto UserSimple para que o Dono do projeto veja o nome/email de quem respondeu.