📑 Referência de API: Módulo de Notificações (Mail)

Este módulo é responsável pela comunicação assíncrona com os usuários, utilizando o protocolo SMTP para disparar alertas críticos do sistema.
🛠️ Configuração Técnica (FastAPI-Mail)

O sistema utiliza a biblioteca fastapi-mail para gerenciar a conexão com o servidor de e-mail.

    Servidor: smtp.gmail.com (Porta 587 - TLS).

    Segurança: As credenciais (MAIL_USERNAME, MAIL_PASSWORD) são carregadas estritamente via variáveis de ambiente (.env), seguindo as recomendações de segurança da LGPD e as práticas do Twelve-Factor App.

📩 Funções de Notificação
1. Convite para Projeto

    Função: send_invitation_email(email_to, project_name)

    Gatilho: Disparado pelo InvitationService quando um OWNER convida um novo colaborador.

    Atendimento ao RF 05: Garante que o colaborador seja notificado sobre sua nova permissão de acesso.

2. Alerta de Nova Resposta

    Função: send_submission_notification(owner_email, project_name, form_title)

    Gatilho: Disparado pelo SubmissionService imediatamente após uma nova submissão ser persistida no banco.

    Atendimento ao RF 15: Mantém o gestor do projeto informado sobre o progresso da coleta de dados em tempo real, sem que ele precise atualizar o dashboard manualmente.