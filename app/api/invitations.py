from fastapi import APIRouter, Depends, status, HTTPException
from app.api.deps import get_current_user
from app.schemas.project_invitation import InvitationCreate, InvitationResponse
from app.services.invitation_service import InvitationService

router = APIRouter(prefix="/invitations", tags=["Convites"])

@router.post("/", response_model=InvitationResponse)
async def send_invite(data: InvitationCreate, user = Depends(get_current_user)):
   
    return await InvitationService.create_invitation(**data.model_dump(), owner_id=user.id)

@router.post("/{invitation_id}/accept")
async def accept_invite(invitation_id: str, user = Depends(get_current_user)):
    return await InvitationService.accept_invitation(invitation_id, user.id, user.email)

@router.get("/me", response_model=list[InvitationResponse])
async def list_my_invitations(user = Depends(get_current_user)):
    """
    Lista todos os convites pendentes para o utilizador logado.
    """
    return await InvitationService.get_my_pending_invitations(user.email)

@router.post("/{invitation_id}/reject")
async def reject_invite(invitation_id: str, user = Depends(get_current_user)):
    """
    Permite ao utilizador recusar um convite, marcando-o como REVOKED.
    """
    # Verificamos se o convite pertence a este utilizador antes de revogar
    invitation = await db.projectinvitation.find_unique(where={"id": invitation_id})
    
    if not invitation or invitation.email != user.email:
        raise HTTPException(status_code=403, detail="Não tem permissão para recusar este convite.")
    
    return await db.projectinvitation.update(
        where={"id": invitation_id},
        data={"status": "REVOKED"}
    )