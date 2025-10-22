from sqlmodel import SQLModel, create_engine, Session

# Nombre del archivo de base de datos SQLite
DATABASE_URL = "sqlite:///./tienda.db"

# Motor de base de datos (engine)
engine = create_engine(DATABASE_URL, echo=True)

# Crear todas las tablas
def init_db():
    SQLModel.metadata.create_all(engine)

# Obtener sesión para interactuar con la base de datos
def get_session():
    with Session(engine) as session:
        yield session
