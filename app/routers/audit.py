from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import AuditLog, User  # ✅ Agregar User aquí
from .auth_router import get_current_user

router = APIRouter(prefix="/audit", tags=["audit"])

@router.get("/history")
def get_audit_history(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)  # ✅ Esto requiere importar User
):
    """Obtiene el historial de eliminaciones (solo admin)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo administradores pueden ver el historial")
    
    logs = session.exec(select(AuditLog).order_by(AuditLog.performed_at.desc())).all()
    return logs