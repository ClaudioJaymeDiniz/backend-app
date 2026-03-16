1. Módulo de Submissões: Camada de Dados (Prisma)

Diferente dos outros modelos, o id da Submission não é gerado pelo banco de dados (PostgreSQL), mas sim injetado pelo cliente (React Native).

Campo	    Tipo	Descrição
id	        String	Chave primária enviada pelo App (UUID) para evitar duplicidade em reenvios offline.
formData	Json	Armazena o par pergunta: resposta de forma flexível.
userId	    String	Vincula a resposta ao aluno/coletor que a enviou.
formId	    String	Identifica a qual formulário aquela resposta pertence.

2. Estratégia de Sincronização (Schemas Pydantic)

O Schema foi projetado para suportar o estado de "desconectado" do celular.
POST /submissions/

Espera no JSON (SubmissionCreate):
{
  "id": "uuid-gerado-no-aparelho-001",
  "formId": "id-do-formulario-escolar",
  "formData": {
    "Nome do Aluno": "Claudio Jayme",
    "Nota da Aula": 10,
    "Gostou da atividade?": "Sim"
  }
}

3. Regras de Negócio e Segurança (SubmissionService)

O serviço implementa uma camada de proteção de dados sensíveis (as respostas dos usuários).

    Garantia de Autoria: O user_id é extraído do token JWT e injetado pelo servidor, impedindo que um usuário envie dados fingindo ser outra pessoa.

    Trava de Edição: O método update_submission contém uma validação lógica: if submission.userId != user_id. Isso garante que apenas o dono da resposta possa corrigi-la.

    Integridade de Sync: Ao aceitar o id vindo do mobile, o sistema permite que, caso a conexão caia e o app tente reenviar o mesmo dado, o Prisma ignore a duplicata (ou atualize) em vez de criar registros repetidos.

4. Endpoints de Coleta (API Routes)

As rotas são otimizadas para o consumo de dados do próprio usuário (perfil "Collector").
A. Enviar Resposta

    Rota: POST /submissions/

    Descrição: Recebe os dados do formulário preenchido.

    Status: 201 Created após o sucesso.

B. Listar Minhas Respostas

    Rota: GET /submissions/me

    Uso no App: Permite que o aluno veja seu histórico de atividades enviadas, mesmo que o formulário original tenha sido deletado pelo professor (os dados da resposta permanecem no formData).

C. Editar Resposta

    Rota: PATCH /submissions/{submission_id}

    Descrição: Permite que o usuário corrija uma resposta enviada anteriormente, desde que ele seja o autor.