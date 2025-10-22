from fastapi import APIRouter, Depends, HTTPException, Form, Cookie, Response, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_session
from ..models import User
from ..auth import verify_password

router = APIRouter(prefix="/auth", tags=["auth"])

# Ruta donde estarán las plantillas HTML
templates = Jinja2Templates(directory="app/templates")

# ------------------------------------------------------------
# 🧩 Mostrar formulario de login (para navegador)
# ------------------------------------------------------------
@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    """Renderiza el formulario de inicio de sesión (HTML)."""
    return templates.TemplateResponse("login.html", {"request": request})

# ------------------------------------------------------------
# 🔐 Procesar login (compatible con Swagger y navegador)
# ------------------------------------------------------------
@router.post("/login")
def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_session)
):
    """Procesa el inicio de sesión (HTML o Swagger)."""
    user = db.query(User).filter(User.username == username).first()

    if not user or not verify_password(password, user.hashed_password):
        # Si es desde navegador, mostrar error en la página HTML
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Usuario o contraseña incorrectos"},
            status_code=401
        )

    # Guardamos cookie (válido para navegador y Swagger)
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="user", value=username, httponly=True)
    return response

# ------------------------------------------------------------
# 🚪 Logout
# ------------------------------------------------------------
@router.get("/logout")
def logout(response: Response):
    """Cierra sesión eliminando cookie"""
    response.delete_cookie(key="user")
    return {"message": "Sesión cerrada"}

# ------------------------------------------------------------
# 👤 Obtener usuario actual (para roles)
# ------------------------------------------------------------
def get_current_user(user: str = Cookie(None), db: Session = Depends(get_session)):
    """Devuelve el usuario autenticado basado en la cookie"""
    if not user:
        raise HTTPException(status_code=401, detail="No autenticado")

    db_user = db.query(User).filter(User.username == user).first()
    if not db_user:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return db_user
