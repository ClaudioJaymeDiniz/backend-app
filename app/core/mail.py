import os
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from dotenv import load_dotenv

load_dotenv()

# Configuração que o FastMail exige
conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD"),
    MAIL_FROM = os.getenv("MAIL_FROM"),
    MAIL_PORT = 587,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)

async def send_invitation_email(email_to: str, project_name: str):
    """
    Envia o e-mail de convite para um novo respondente.
    Atende ao RF 05.
    """
    message = MessageSchema(
        subject=f"Convite: Projeto {project_name}",
        recipients=[email_to],
        body=f"Olá! Você foi convidado para colaborar no projeto '{project_name}'. Acesse o app para responder.",
        subtype=MessageType.plain
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)


async def send_submission_notification(owner_email: str, project_name: str, form_title: str):
    """
    Notifica o dono do projeto sobre uma nova submissão.
    Atende ao RF 15.
    """
    message = MessageSchema(
        subject=f"Nova Resposta: {form_title}",
        recipients=[owner_email],
        body=f"Olá!\n\nO formulário '{form_title}' do projeto '{project_name}' recebeu uma nova resposta.\n\nAcesse o dashboard para visualizar os dados.",
        subtype=MessageType.plain
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)