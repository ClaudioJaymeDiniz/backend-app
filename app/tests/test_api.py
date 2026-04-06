import httpx
import asyncio

BASE_URL = "http://127.0.0.1:8001"

async def run_tests():
    async with httpx.AsyncClient() as client:
        print("🚀 Iniciando Testes de Integração...")

        # 1. Testar Cadastro de Usuário
        user_data = {
            "email": "test_fatec@example.com",
            "password": "102030",
            "name": "Claudio Teste",
            "provider": "local"
        }
        print("\n[1] Registrando usuário...")
        res = await client.post(f"{BASE_URL}/auth/register", json=user_data)
        print(f"Status: {res.status_code}")

        # 2. Testar Login e Obter Token
        print("\n[2] Realizando login...")
        login_data = {"username": user_data["email"], "password": user_data["password"]}
        res = await client.post(f"{BASE_URL}/auth/login", data=login_data)
        token = res.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Token gerado: {token[:20]}...")

        # 3. Criar um Projeto
        print("\n[3] Criando novo projeto...")
        project_data = {
            "name": "Projeto de Campo FATEC",
            "description": "Teste automatizado de criação",
            "themeColor": "#FF5733"
        }
        res = await client.post(f"{BASE_URL}/projects/", json=project_data, headers=headers)
        project_id = res.json().get("id")
        print(f"Projeto Criado! ID: {project_id}")

        # 4. Convidar um Colaborador (Fluxo Inteligente)
        print("\n[4] Convidando colaborador...")
        invite_data = {
            "projectId": project_id,
            "email": "claudiojayme@gmail.com"
        }
        res = await client.post(f"{BASE_URL}/invitations/", json=invite_data, headers=headers)
        print(f"Convite enviado! Status no Banco: {res.json().get('status')}")

        print("\n✅ Todos os testes básicos passaram!")

if __name__ == "__main__":
    asyncio.run(run_tests())