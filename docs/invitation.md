Tens toda razão, Claudio. O módulo de Convites (Invitations) é o que amarra a colaboração entre os usuários no seu TCC. Ele é a ponte entre o anonimato de um e-mail e a permissão real de acesso dentro do banco de dados.

Aqui está o detalhamento técnico completo das rotas de convite, já integrando a lógica "inteligente" que discutimos (usuário cadastrado vs. novo usuário).
📑 Referência de API: Módulo de Convites (ProjectInvitation)

Este módulo gerencia as permissões de acesso aos projetos. Ele implementa o RF 05 (Convite por e-mail) e o RF 17 (Controle de acesso por cargo).
🛠️ Service: InvitationService

A lógica de negócio aqui é "reativa": ela verifica a existência do usuário antes de decidir o status do convite.

    create_invitation:

        Verifica se o e-mail já possui um convite para aquele projeto (evita duplicidade).

        Verifica se o e-mail pertence a um User já cadastrado.

        Se sim: Cria o registro em UserProject (acesso imediato) e marca o convite como ACCEPTED.

        Se não: Marca como PENDING e dispara o serviço de e-mail (send_invitation_email).

    check_access: Função utilitária usada por outras rotas (como as de Forms e Submissions) para validar se o e-mail do usuário logado tem permissão de COLLECTOR ou OWNER.

🚀 Rotas e Endpoints (/invitations)
1. Convidar Colaborador

    Rota: POST /invitations/

    Entrada: InvitationCreate (E-mail e ProjectId).

    Regra de Segurança: Apenas o OWNER do projeto pode disparar esta rota.

    Resposta: Retorna o objeto do convite com o status (se foi aceito automaticamente ou ficou pendente).

2. Listar Meus Convites Pendentes

    Rota: GET /invitations/me

    Descrição: Retorna todos os convites com status PENDING enviados para o e-mail do usuário logado.

    Uso no App: Alimenta a aba "Notificações" ou "Convites Recebidos" no Mobile.

3. Aceitar Convite (Manual)

    Rota: POST /invitations/{invitation_id}/accept

    Ação: 1.  Muda o status para ACCEPTED.
    2.  Cria o vínculo na tabela UserProject.

    Contexto: Usado principalmente para usuários que se cadastraram após terem recebido o e-mail de convite.

4. Revogar Acesso / Deletar Convite

    Rota: DELETE /invitations/{invitation_id}

    Descrição: Remove o convite e, consequentemente, remove a entrada correspondente na tabela UserProject.

    Regra: Apenas o dono do projeto pode revogar acessos.

📊 Tabela de Estados do Convite
Status	Condição	Acesso ao Projeto?
PENDING	E-mail enviado, mas usuário não cadastrado ou não aceitou.	Não
ACCEPTED	Usuário já vinculado via UserProject.	Sim
REVOKED	Acesso removido pelo administrador.	Não