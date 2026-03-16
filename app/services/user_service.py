from app.core.prisma_client import db
from app.core.security import get_password_hash
from app.schemas.user import UserCreate, UserUpdate

class UserService:
    @staticmethod
    async def create_user(user_in: UserCreate):
        hashed_password = get_password_hash(user_in.password)
        return await db.user.create(
            data={
                "email": user_in.email,
                "name": user_in.name,
                "password": hashed_password,
                "provider": "local"
            }
        )

    @staticmethod
    async def get_by_email(email: str):
        return await db.user.find_unique(where={"email": email})

    @staticmethod
    async def get_by_id(user_id: str):
        return await db.user.find_unique(where={"id": user_id})
    
    @staticmethod
    async def update_user(user_id: str, user_in: UserUpdate):
        update_data = user_in.model_dump(exclude_unset=True)
        
        # Se houver senha nova, precisamos criptografar
        if "password" in update_data:
            update_data["password"] = get_password_hash(update_data["password"])
            
        return await db.user.update(
            where={"id": user_id},
            data=update_data
        )

    @staticmethod
    async def delete_user(user_id: str):
        return await db.user.delete(where={"id": user_id})