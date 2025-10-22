from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """Genera un hash seguro para guardar en base de datos"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Verifica si la contraseña ingresada coincide con el hash"""
    return pwd_context.verify(plain_password, hashed_password)
