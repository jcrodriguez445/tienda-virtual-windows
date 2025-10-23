from fastapi import FastAPI
from .database import init_db
from .models import User, Product, AuditLog # ✅ corregido: antes decía Item
from .routers import users, auth_router, products, audit

app = FastAPI()

# Inicializar base de datos al arrancar
@app.on_event("startup")
def on_startup():
    init_db()

# Incluir rutas
app.include_router(users.router)
app.include_router(auth_router.router)
app.include_router(products.router)
app.include_router(audit.router)

@app.get("/")
def read_root():
    return {"message": "Base de datos inicializada y servidor corriendo correctamente."}

@app.get("/")
def simple_test():
    return {"message": "Test simple - sin base de datos"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)

