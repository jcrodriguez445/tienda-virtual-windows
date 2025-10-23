from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from ..database import get_session
from ..models import Product, User, AuditLog
from ..routers.auth_router import get_current_user  # para saber quién está logueado

router = APIRouter(prefix="/products", tags=["products"])

# ======================================================
# 🟢 Crear producto (solo admin)
# ======================================================
@router.post("/create")
def create_product(
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    quantity: int = Form(...),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden crear productos")

    product = Product(
        name=name,
        description=description,
        price=price,
        quantity=quantity,
        owner_id=current_user.id
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"message": "Producto creado exitosamente", "product": product}


# ======================================================
# 🔵 Listar todos los productos (clientes y admin)
# ======================================================
@router.get("/list", response_model=List[Product])
def list_products(db: Session = Depends(get_session)):
    products = db.query(Product).all()
    return products


# ======================================================
# 🟠 Actualizar producto (solo admin)
# ======================================================
@router.put("/{product_id}")
def update_product(
    product_id: int,
    name: str = Form(None),
    description: str = Form(None),
    price: float = Form(None),
    quantity: int = Form(None),
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden actualizar productos")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if name:
        product.name = name
    if description:
        product.description = description
    if price is not None:
        product.price = price
    if quantity is not None:
        product.quantity = quantity

    db.commit()
    db.refresh(product)
    return {"message": "Producto actualizado correctamente", "product": product}


# ======================================================
# 🔴 Eliminar producto (solo admin) - CON HISTORIAL
# ======================================================
@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Solo los administradores pueden eliminar productos")

    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # 🔥 REGISTRAR EN HISTORIAL ANTES de eliminar
    audit_log = AuditLog(
        action="DELETE_PRODUCT",
        target_id=product_id,
        target_name=product.name,
        performed_by=current_user.username,
        details=f"Producto '{product.name}' (Precio: ${product.price}, Cantidad: {product.quantity}) eliminado por {current_user.username}"
    )
    db.add(audit_log)
    
    db.delete(product)
    db.commit()
    return {"message": f"Producto '{product.name}' eliminado exitosamente"}

    # ======================================================
# 🔍 VER INFORMACIÓN DEL DUEÑO DE UN PRODUCTO
# ======================================================
@router.get("/{product_id}/owner")
def get_product_owner(
    product_id: int,
    db: Session = Depends(get_session)
):
    """Obtiene información del usuario dueño de un producto"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    if not product.owner:
        return {"message": "Este producto no tiene dueño asignado"}
    
    return {
        "owner_id": product.owner.id,
        "owner_username": product.owner.username,
        "owner_role": product.owner.role,
        "owner_created_at": product.owner.created_at
    }