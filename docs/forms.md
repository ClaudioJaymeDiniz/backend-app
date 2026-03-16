1. Módulo de Formulários: Camada de Dados (Prisma)

O diferencial aqui é o uso do tipo Json para o campo structure. Enquanto bancos de dados tradicionais exigem tabelas rígidas, o PostgreSQL (via Prisma) permite armazenar objetos complexos, garantindo a natureza "Smart" do projeto.

Campo	    Tipo	        Descrição
id	        String(UUID)	Identificador único do formulário.
title	    String	        Nome do formulário (Ex: "Ficha de Inscrição").
structure	Json	        O coração do sistema. Armazena a lista de campos, tipos e regras de validação.
projectId	String	        Chave estrangeira que vincula o formulário a um projeto específico.

2. Camada de Validação (Schemas Pydantic)

O FormField define o contrato para cada campo que aparecerá no React Native.
POST /forms/

Espera no JSON (FormCreate):
{
  "title": "Avaliação de Oficina",
  "description": "Feedback dos alunos sobre a aula de Stop Motion",
  "projectId": "id-do-projeto-aqui",
  "fields": [
    {
      "label": "Nome do Aluno",
      "type": "text",
      "required": true
    },
    {
      "label": "Nota da Aula",
      "type": "number",
      "required": true
    },
    {
      "label": "Gostou da atividade?",
      "type": "select",
      "options": ["Sim", "Não", "Mais ou menos"]
    }
  ]
}
3. Camada de Inteligência (FormService)

O FormService atua como um guardião de integridade e segurança.

    Mapeamento Automático: Ele transforma a lista de objetos fields do Python em um formato Json puro para o Prisma.

    Validação de Propriedade: Antes de criar ou excluir um formulário, ele verifica se o projectId realmente pertence ao user_id logado.

    Agregação de Resultados: O método get_all_submissions_for_form realiza um join complexo para trazer não apenas as respostas, mas também os nomes dos alunos que responderam, facilitando a vida do professor.

4. Endpoints de Interação (API Routes)

As rotas foram desenhadas para suportar tanto o fluxo do Professor (Dono) quanto o do Aluno (Coletor).
A. Listar Formulários do Projeto

    Rota: GET /forms/project/{project_id}

    Uso no App: Carrega a lista de atividades disponíveis para aquela oficina específica.

B. Dashboard de Resultados (Dono apenas)

    Rota: GET /forms/{form_id}/results

    Segurança: Se um aluno tentar acessar esta rota, o FormService disparará um erro 403 Forbidden.

    Resposta: Retorna um array com todas as submissões e os dados dos usuários que as enviaram.

5. Destaque Técnico para o TCC: "Schemaless-on-SQL"

Explique para a banca que você utilizou uma técnica de Esquema Dinâmico.

    O Backend não precisa saber quais campos o formulário tem.

    O React Native lê o JSON structure, percorre a lista e renderiza os componentes de input (TextInput, Picker, Switch) em tempo de execução.

    Isso reduz drasticamente o custo de manutenção do software.