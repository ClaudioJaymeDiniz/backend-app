1. Módulo de Usuário: Camada de Dados (Prisma)

O modelo User é a base de toda a aplicação. Ele utiliza UUID para identificação única, o que aumenta a segurança ao não expor IDs sequenciais.

Campo	        Tipo	        Descrição
id	            String(UUID)	Chave primária gerada automaticamente.
email	        String	        E-mail único utilizado para login.
password	    String	        Hash da senha (armazenado via Bcrypt).
provider	    String	        Origem do login (local, google, facebook).
globalMetadata	Json	        Campo flexível para configurações globais do usuário.

2. Camada de Validação (Schemas Pydantic)

Os Schemas garantem que o JSON enviado pelo usuário esteja correto antes de chegar ao banco de dados.
POST /auth/register

Espera no JSON (UserCreate):
{
  "email": "professor@fatec.sp.gov.br",
  "name": "Claudio Jayme",
  "password": "senha_segura_aqui",
  "provider": "local"
}

PATCH /auth/me

Espera no JSON (UserUpdate):
(Todos os campos são opcionais - envie apenas o que quer mudar)
{
  "name": "Claudio J. Atualizado",
  "password": "nova_senha_opcional",
  "globalMetadata": { "tema": "dark" }
}

3. Camada de Serviço (UserService)

O UserService centraliza as regras de negócio. É aqui que a senha é transformada em Hash antes de ser salva.

    create_user: Recebe os dados brutos, aplica o hash na senha e persiste no banco.

    update_user: Utiliza exclude_unset=True para atualizar apenas os campos enviados, protegendo os dados existentes.

    get_by_email / get_by_id: Métodos auxiliares para busca e validação de existência.

4. Endpoints de Autenticação (API Routes)

Aqui estão as rotas que o seu app React Native irá consumir.
A. Registro de Usuário

    Rota: POST /auth/register

    Sucesso (200 OK): Retorna o objeto UserResponse (sem a senha).

    Erro (400): Se o e-mail já existir.

B. Login (Geração de Token)

    Rota: POST /auth/login

    Formato de envio: x-www-form-urlencoded (Padrão OAuth2).

    Campos: username (e-mail) e password.

    Retorno:
    {
        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "token_type": "bearer"
    }      
C. Perfil do Usuário

    Rota: GET /auth/me

    Requisito: Requer Header Authorization: Bearer <token>.

    Descrição: Retorna os dados completos do usuário logado (id, e-mail, nome, metadata).

5. Fluxo de Segurança

O sistema utiliza JWT (JSON Web Token). O fluxo funciona assim:

    O usuário envia credenciais.

    O servidor valida e devolve um Token assinado.

    O App Mobile guarda esse token.

    Para acessar /me ou criar projetos, o App envia o token no cabeçalho.

    O deps.py intercepta, decodifica o sub (ID do usuário) e injeta o objeto current_user na função da rota.