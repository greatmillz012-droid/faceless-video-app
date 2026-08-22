from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from .. import auth, models
from ..database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


class RegisterIn(BaseModel):
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    email = (payload.email or "").strip()
    password = payload.password or ""

    if not email:
        raise HTTPException(400, "Email is required")

    if not password:
        raise HTTPException(400, "Password is required")

    if len(password) < 6:
        raise HTTPException(400, "Password must be at least 6 characters")

    existing = db.query(models.User).filter(models.User.email == email).first()
    if existing:
        raise HTTPException(400, "Email already registered")

    try:
        user = models.User(
            email=email,
            hashed_password=auth.hash_password(password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        settings_row = models.UserSettings(user_id=user.id)
        db.add(settings_row)
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(500, "Could not create account")

    token = auth.create_access_token({"sub": user.email})
    return {
        "message": "Account created successfully",
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/login")
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not auth.verify_password(payload.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")

    token = auth.create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me")
def get_me(user: models.User = Depends(auth.get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }
