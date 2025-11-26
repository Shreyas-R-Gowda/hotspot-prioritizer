from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .. import models, schemas, database
from ..deps.roles import get_db, require_role
from .auth import get_password_hash

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users", response_model=List[schemas.UserResponse])
def list_users(
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    users = db.query(models.User).all()
    return users

@router.post("/users", response_model=schemas.UserResponse)
def create_admin_user(
    user: schemas.UserCreate,
    current_user: models.User = Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_admin = models.User(
        email=user.email,
        name=user.name,
        password_hash=hashed_password,
        role="admin"
    )
    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)
    return new_admin
