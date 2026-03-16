from datetime import datetime, timedelta, timezone
from jose import jwt
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Pega as variáveis de ambiente
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))
# Configura o passlib para usar bcrypt
# O "rounds" define a complexidade (custo computacional). 12 é um ótimo equilíbrio.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Transforma a senha em um hash seguro para salvar no banco."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compara uma senha digitada com o hash salvo no banco."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """Gera um token JWT com data de expiração."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt