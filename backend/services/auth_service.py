from datetime import datetime, timedelta, timezone
from jose import jwt
from passlib.context import CryptContext
from fastapi import HTTPException
import secrets
from datetime import datetime, timedelta

from backend.core.config import settings
from backend.repositories import auth_repo

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def registrar_usuario(db, nombre: str, email: str, password: str, nombre_comercio: str):
    existente = auth_repo.obtener_usuario_por_email(db, email)
    if existente:
        raise HTTPException(status_code=400, detail="Ya existe un usuario con ese email")

    comercio = auth_repo.crear_comercio_para_usuario(db, nombre_comercio, email)

    password_hash = hash_password(password)

    usuario = auth_repo.crear_usuario(
        db,
        nombre,
        email,
        password_hash,
        comercio["id"]
    )

    access_token = create_access_token({
        "sub": str(usuario["id"]),
        "email": usuario["email"],
        "comercio_id": usuario["comercio_id"],
    })

    refresh_token = secrets.token_hex(32)

    expires_at = datetime.utcnow() + timedelta(days=7)

    auth_repo.crear_refresh_token(
        db,
        usuario["id"],
        refresh_token,
        expires_at
    )

    return {
        "usuario": usuario,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


def login_usuario(db, email: str, password: str):
    usuario = auth_repo.obtener_usuario_por_email(db, email)

    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if not verify_password(password, usuario["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    token = create_access_token({
        "sub": str(usuario["id"]),
        "email": usuario["email"],
        "comercio_id": usuario["comercio_id"],
    })

    refresh_token = secrets.token_hex(32)

    expires_at = datetime.utcnow() + timedelta(days=7)

    auth_repo.crear_refresh_token(
        db,
        usuario["id"],
        refresh_token,
        expires_at
    )

    return {
        "access_token": token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
    
def refresh_access_token(db, refresh_token: str):
    token_db = auth_repo.obtener_refresh_token(db, refresh_token)

    if not token_db:
        raise ValueError("Refresh token inválido")

    if token_db["revoked"]:
        raise ValueError("Refresh token revocado")

    if token_db["expires_at"] < datetime.utcnow():
        raise ValueError("Refresh token expirado")

    usuario_id = token_db["usuario_id"]

    nuevo_access_token = create_access_token({
        "sub": str(usuario_id),
    })

    return {
        "access_token": nuevo_access_token,
        "token_type": "bearer",
    }
    
def logout(db, refresh_token: str):
    auth_repo.revocar_refresh_token(db, refresh_token)