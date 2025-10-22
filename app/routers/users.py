from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from ..database import get_session
from ..models import User
from ..auth import hash_password
from .auth_router import get_current_user  # Para verificar rol

router = APIRouter(prefix="/users", tags=["users"])

# Crear usuario
@router.post("/", response_model=User)
def create_user(user: User, session: Session = Depends(get_session)):
    # Verificar si el usuario ya existe
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe.")

    # Hashear la contraseña antes de guardar
    user.hashed_password = hash_password(user.hashed_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Listar todos los usuarios (solo admin)
@router.get("/", response_model=List[User])
def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver esta lista."
        )

    users = session.exec(select(User)).all()
    return users

# Actualizar usuario (solo admin)
@router.put("/{user_id}", response_model=User)
def update_user(
    user_id: int,
    updated_user: User,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Solo los administradores pueden editar usuarios
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para editar usuarios")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizamos los campos básicos
    user.username = updated_user.username
    user.role = updated_user.role

    # Solo actualiza contraseña si se pasa una nueva
    if updated_user.hashed_password:
        from ..auth import hash_password
        user.hashed_password = hash_password(updated_user.hashed_password)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

# Eliminar usuario (solo admin)
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Solo los administradores pueden eliminar usuarios
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="No tienes permisos para eliminar usuarios")

    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    session.delete(user)
    session.commit()
    return {"message": f"Usuario '{user.username}' eliminado correctamente"}
