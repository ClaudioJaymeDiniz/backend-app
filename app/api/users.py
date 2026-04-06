from fastapi import APIRouter, Depends, Query, HTTPException
from typing import List
from app.api.deps import get_current_user
from app.core.prisma_client import db
from app.schemas.user import UserSimple

router = APIRouter(prefix="/users", tags=["Usuários"])

@router.get("/search", response_model=List[UserSimple])
async def search_users(
    q: str = Query(..., min_length=3),
    current_user = Depends(get_current_user)
):
    try:  
        termo = q.strip()

        users = await db.user.find_many(
            where={
                "OR": [
                    {
                        "name": {
                            "contains": termo,
                            "mode": "insensitive"
                        }
                    },
                    {
                        "email": {
                            "contains": termo,
                            "mode": "insensitive"
                        }
                    }
                ],
                # Impede que você convide a si mesmo
                "NOT": {"id": current_user.id}
            },
            take=10
        )
        return users

    except Exception as e:
        print(f"Erro na busca: {e}") 
        raise HTTPException(
            status_code=500, 
            detail="Erro interno ao buscar usuários"
        )