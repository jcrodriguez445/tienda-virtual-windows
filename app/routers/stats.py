from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, func
from typing import List, Dict, Any
from ..database import get_session
from ..models import User, Product
from .auth_router import get_current_user

router = APIRouter(prefix="/stats", tags=["stats"])

@router.get("/user-products")
def get_user_products_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Estadísticas de productos por usuario (solo admin)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Solo los administradores pueden ver las estadísticas"
        )
    
    users = session.exec(select(User)).all()
    
    stats = []
    for user in users:
        product_count = len(user.products)
        total_value = sum(product.price * product.quantity for product in user.products)
        
        stats.append({
            "user_id": user.id,
            "username": user.username,
            "role": user.role,
            "product_count": product_count,
            "total_inventory_value": total_value,
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "quantity": product.quantity,
                    "total_value": product.price * product.quantity
                } for product in user.products
            ]
        })
    
    # Ordenar por mayor cantidad de productos
    stats.sort(key=lambda x: x["product_count"], reverse=True)
    
    return {
        "total_users": len(users),
        "total_products": sum(stat["product_count"] for stat in stats),
        "total_inventory_value": sum(stat["total_inventory_value"] for stat in stats),
        "users_stats": stats
    }

@router.get("/general")
def get_general_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Estadísticas generales del sistema (solo admin)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Solo los administradores pueden ver las estadísticas"
        )
    
    # Contar usuarios por rol
    users = session.exec(select(User)).all()
    admin_count = sum(1 for user in users if user.role == "admin")
    client_count = sum(1 for user in users if user.role == "client")
    
    # Estadísticas de productos
    products = session.exec(select(Product)).all()
    total_products = len(products)
    products_with_owner = sum(1 for product in products if product.owner_id is not None)
    
    # Producto más caro
    most_expensive = max(products, key=lambda x: x.price) if products else None
    # Producto con mayor cantidad
    most_quantity = max(products, key=lambda x: x.quantity) if products else None
    
    return {
        "users": {
            "total": len(users),
            "admins": admin_count,
            "clients": client_count
        },
        "products": {
            "total": total_products,
            "with_owner": products_with_owner,
            "without_owner": total_products - products_with_owner,
            "total_inventory_value": sum(product.price * product.quantity for product in products),
            "most_expensive_product": {
                "id": most_expensive.id if most_expensive else None,
                "name": most_expensive.name if most_expensive else None,
                "price": most_expensive.price if most_expensive else None
            } if most_expensive else None,
            "most_stocked_product": {
                "id": most_quantity.id if most_quantity else None,
                "name": most_quantity.name if most_quantity else None,
                "quantity": most_quantity.quantity if most_quantity else None
            } if most_quantity else None
        }
    }