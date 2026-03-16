import asyncio
from app.core.mail import send_invitation_email

async def test():
    print("Tentando enviar e-mail de teste...")
    try:
        await send_invitation_email("seu-proprio-email@gmail.com", "Projeto de Teste FATEC")
        print("✅ E-mail enviado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao enviar: {e}")

if __name__ == "__main__":
    asyncio.run(test())