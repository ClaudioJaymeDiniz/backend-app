1. Módulo de Projetos: Camada de Dados (Prisma)

O modelo Project armazena as configurações estruturais e visuais de um agrupamento de formulários. A tabela UserProject gerencia a relação N:N (muitos para muitos), permitindo que usuários tenham papéis específicos (OWNER ou COLLECTOR) em cada projeto.

Campo	                Tipo	    Descrição
themeColor	            String	    Código Hexadecimal (ex: #3B82F6) que define a cor principal da interface no App.
logoUrl	                String?	    Caminho ou URL da imagem que será exibida como marca do projeto.
isPublic	            Boolean	    Define se o projeto pode ser acessado por qualquer pessoa ou apenas convidados.
projectSpecificMetadata	Json	    (Em UserProject) Dados contextuais do usuário no projeto, como "Matrícula" ou "Escola".

2. Camada de Validação (Schemas Pydantic)

Aqui, utilizamos Regex (Padrões de Texto) via Field para garantir que as cores enviadas sejam hexadecimais válidos, evitando erros de renderização no React Native.
POST /projects/

Espera no JSON (ProjectCreate):
{
  "name": "Oficina de Robótica 2026",
  "description": "Projeto focado em Arduino e automação.",
  "isPublic": true,
  "themeColor": "#E11D48",
  "logoUrl": "/uploads/logo-robotica.png"
}

PATCH /projects/{project_id}

Espera no JSON (ProjectUpdate):
(Permite atualização parcial. Exemplo: mudar apenas a cor)
{
  "themeColor": "#22C55E"
}

3. Endpoints de Gerenciamento (API Routes)

As rotas de projeto são protegidas. O sistema identifica automaticamente quem é o dono através do token JWT.
A. Criar Novo Projeto

    Rota: POST /projects/

    Requisito: Usuário autenticado.

    Ação: Vincula o id do usuário logado ao campo ownerId do projeto.

B. Listar Meus Projetos

    Rota: GET /projects/

    Retorno: Uma lista (Array) de projetos onde o usuário é o dono.

    Exemplo de uso no App: Preencher a tela inicial com os cards personalizados de cada oficina.

C. Atualizar Projeto

    Rota: PATCH /projects/{project_id}

    Segurança: Verifica se o project_id existe e se o ownerId coincide com o usuário do token. Caso contrário, retorna 404 Not Found (por segurança, para não confirmar a existência de um ID para estranhos).

4. Lógica de Personalização (Dynamic Theming)

Este é um ponto técnico forte para sua documentação de TCC. Explique que o backend não renderiza a interface, mas fornece os metadados visuais necessários.

    Requisição: O App Mobile solicita os dados do projeto.

    Resposta: O backend envia o themeColor e logoUrl.

    Consumo: O React Native recebe esses valores e os injeta dinamicamente nos estilos (CSS-in-JS), permitindo que uma única base de código suporte múltiplas identidades visuais sem recompilação.