📑 Documentação de API: Módulo de Usuário (User)

Este módulo gerencia o ciclo de vida dos usuários, desde o registro até a atualização de metadados globais e exclusão da conta.
🗄️ Modelo de Dados (Prisma Entity)

O usuário é a entidade central. No banco de dados PostgreSQL, ele é representado da seguinte forma:
Campo	Tipo	Descrição
id	String (UUID)	Chave primária única.
email	String	E-mail único usado para login.
name	String?	Nome completo (opcional).
password	String?	Hash da senha (armazenado apenas para login local).
provider	String	Origem da conta (local, google, facebook).
globalMetadata	Json?	Metadados genéricos do usuário.
createdAt	DateTime	Timestamp de criação automática.
🛠️ Service: UserService

Camada de lógica que interage com o Prisma Client.

    create_user(user_in: UserCreate): Criptografa a senha usando bcrypt via get_password_hash e persiste o usuário.

    get_by_email(email: str): Busca rápida para autenticação.

    get_by_id(user_id: str): Busca para resolução de dependências e perfil.

    update_user(user_id: str, user_in: UserUpdate): Atualiza campos parciais. Se uma nova senha for enviada, ela é hasheada automaticamente.

    delete_user(user_id: str): Remove permanentemente o registro (Hard Delete).

🚀 Rotas e Endpoints (FastAPI)
1. Registro de Usuário

POST /users/register (ou conforme sua rota de auth)

    Descrição: Cria uma nova conta no sistema.

    Body (Schema: UserCreate):

    {
  "email": "exemplo@email.com",
  "password": "senha_segura",
  "name": "Claudio Jayme"
}
Resposta: UserResponse (201 Created).

2. Obter Perfil Atual

GET /users/me

    Requisito: Dependência get_current_user (Bearer Token).

    Descrição: Retorna os dados do usuário autenticado.

    Resposta: UserResponse.

3. Atualizar Dados

PATCH /users/me

    Body (Schema: UserUpdate):

        name: string (opcional)

        password: string (opcional)

        globalMetadata: objeto json (opcional)

    Função: O exclude_unset=True no service garante que apenas os campos enviados sejam alterados.

🔐 Schemas de Validação (Pydantic)

A documentação de tipos garante a integridade dos dados trafegados:
Classe	Finalidade	Campos Principais
UserCreate	Ingestão de dados	email (validado), password (raw), name.
UserUpdate	Edição parcial	password (opcional), globalMetadata (dict).
UserResponse	Resposta da API	id, createdAt. Nunca inclui password.
UserSimple	Relacionamentos	Versão leve para listas e convites (id, name, email).


Documentação de API: Fluxo de Autenticação (Auth)

Este módulo gerencia o acesso seguro ao sistema, controle de sessões via tokens e recuperação de contas.
🛡️ Estratégia de Segurança

    Hash de Senhas: Utiliza bcrypt para garantir que senhas nunca sejam armazenadas em texto plano.

    Tokens de Acesso: Implementa JWT (JSON Web Tokens) com tempo de expiração, garantindo que as requisições ao Linux Mint sejam autenticadas.

    Dependency Injection: Utiliza a função get_current_user como um "guardião" em rotas protegidas.

🚀 Endpoints de Autenticação
1. Registro de Novo Usuário

POST /auth/register

    Descrição: Cria uma conta vinculada ao provedor local.

    Regra de Negócio: Verifica se o e-mail já existe na base do Prisma antes de prosseguir.

    Resposta: UserResponse (sem a senha).

2. Login e Geração de Token

POST /auth/login

    Entrada: username (e-mail) e password via OAuth2PasswordRequestForm.

    Processamento:

        Busca o usuário por e-mail.

        Verifica o hash da senha.

        Gera um JWT contendo o id e email no payload (sub).

    Resposta: ```json
    {
    "access_token": "eyJhbG...",
    "token_type": "bearer"
    }

    3. Gestão do Perfil Próprio (/me)
Rota	Método	Descrição
/auth/me	GET	Retorna os dados completos do usuário dono do token.
/auth/me	PATCH	Permite que o usuário atualize seu nome, senha ou metadados.
4. Recuperação de Senha (Fluxo de 2 Etapas)

    Etapa 1: POST /auth/recover-password

        Gera um uuid4 como token de uso único.

        Armazena o token e a expiração (1 hora) no campo globalMetadata do JSON no PostgreSQL.

        Nota para o TCC: Demonstra o uso versátil de campos JSON para evitar a criação excessiva de tabelas simples.

    Etapa 2: POST /auth/reset-password

        Valida o token via busca no JSON.

        Verifica se o token ainda é válido (data de expiração).

        Atualiza a senha e limpa o token do metadado por segurança.

        Com certeza, Claudio. Vamos detalhar o módulo de Usuário e Autenticação (User & Auth) com o mesmo nível de rigor técnico, separando as rotas de gerenciamento de conta das rotas de segurança (Login/Token).

Para o seu TCC, essa separação demonstra que você entende a diferença entre Identidade (quem o usuário é) e Acesso (o que o usuário pode fazer).
📑 Referência de API: Módulo de Usuário e Autenticação

Este módulo é dividido em dois controladores: /auth (Segurança e Sessão) e o suporte do UserService (Persistência).
🔐 1. Endpoints de Autenticação (/auth)

Gerencia o ciclo de vida da sessão e a segurança da conta.
1.1 Registrar Novo Usuário

    Rota: POST /auth/register

    Entrada: UserCreate (email, password, name).

    Validação: Verifica via UserService.get_by_email se o e-mail já existe.

    Segurança: A senha é hasheada no Service antes de tocar o banco de dados.

1.2 Login (Geração de Token)

    Rota: POST /auth/login

    Entrada: OAuth2PasswordRequestForm (username/password).

    Processamento: 1. verify_password: Compara o hash do banco com a senha enviada.
    2. create_access_token: Gera um JWT com o ID e Email.

    Resposta: Objeto contendo o access_token e o token_type: bearer.

1.3 Obter Meu Perfil

    Rota: GET /auth/me

    Requisito: Bearer Token válido.

    Descrição: Retorna os dados do usuário dono do token atual (current_user). Útil para sincronizar o estado do App no mobile.

1.4 Atualizar Meu Perfil

    Rota: PATCH /auth/me

    Entrada: UserUpdate (campos opcionais).

    Descrição: Permite alterar nome, senha ou globalMetadata. Se a senha for alterada, um novo hash é gerado automaticamente.

1.5 Recuperação de Senha (Solicitação)

    Rota: POST /auth/recover-password

    Entrada: PasswordRecoveryRequest (email).

    Lógica: 1. Gera um UUID único como token.
    2. Grava o token e a expiração (ISO String) dentro do campo JSON globalMetadata.

    Segurança: Retorna uma mensagem genérica mesmo que o e-mail não exista (evita User Enumeration).

1.6 Reset de Senha (Confirmação)

    Rota: POST /auth/reset-password

    Entrada: PasswordReset (token, new_password).

    Lógica: 1. Busca o usuário que possui aquele token exato dentro do JSON globalMetadata.
    2. Valida se o tempo atual é menor que reset_token_expires.
    3. Atualiza a senha e remove as chaves de token do JSON para invalidar o uso repetido.

    Função,Parâmetros,Descrição Técnica
create_user,UserCreate,Aplica get_password_hash e db.user.create.
get_by_email,email: str,Busca indexada via @unique no Prisma.
update_user,"id, UserUpdate",Usa model_dump(exclude_unset=True) para updates parciais.
delete_user,id: str,db.user.delete (Hard Delete).