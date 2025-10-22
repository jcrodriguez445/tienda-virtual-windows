from fastapi import FastAPI
from .database import init_db
from .models import User, Item
from .routers import users, auth_router

app = FastAPI()

# Inicializar base de datos al arrancar
@app.on_event("startup")
def on_startup():
    init_db()

# Incluir rutas
app.include_router(users.router)
app.include_router(auth_router.router)


@app.get("/")
def read_root():
    return {"message": "Base de datos inicializada y servidor corriendo correctamente."}
