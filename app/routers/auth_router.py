from fastapi import APIRouter, Depends, HTTPException, Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from ..database import get_session
from ..models import User
from ..auth import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

# ------------------------------------------------------------
# 🧩 Mostrar formulario de login
# ------------------------------------------------------------
@router.get("/login", response_class=HTMLResponse)
def login_form():
    return """
    <h2>Iniciar sesión</h2>
    <form action="/auth/login" method="post">
        <input type="text" name="username" placeholder="Usuario" required><br>
        <input type="password" name="password" placeholder="Contraseña" required><br>
        <button type="submit">Ingresar</button>
    </form>
    """

# ------------------------------------------------------------
# 🔐 Procesar login
# ------------------------------------------------------------
@router.post("/login")
def login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_session)):
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")

    # Guardamos el usuario en cookie
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="user", value=username)
    return response

# ------------------------------------------------------------
# 🚪 Logout
# ------------------------------------------------------------
@router.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(key="user")
    return response

# ------------------------------------------------------------
# 👤 Obtener usuario actual (para roles)
# ------------------------------------------------------------
def get_current_user(user: str = Cookie(None), db: Session = Depends(get_session)):
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    db_user = db.query(User).filter(User.username == user).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return db_user
