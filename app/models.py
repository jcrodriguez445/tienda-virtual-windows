from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 👇 NUEVO: campo de rol
    role: str = Field(default="client")  # puede ser "admin" o "client"

    # Relación con los ítems (uno a muchos)
    items: List["Item"] = Relationship(back_populates="owner")

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    price: float
    image_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")

    # Relación inversa (dueño del item)
    owner: Optional[User] = Relationship(back_populates="items")
