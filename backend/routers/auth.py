from jose import jwt, JWTError
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.schemas.clase_auth import RefreshRequest
from backend.database import get_db
from backend.schemas.clase_auth import UsuarioRegistro, UsuarioLogin, TokenResponse, UsuarioOut
from backend.services import auth_service
from backend.repositories import auth_repo
from backend.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

security = HTTPBearer()


@router.post("/register", status_code=201)
def register(data: UsuarioRegistro, db=Depends(get_db)):
    return auth_service.registrar_usuario(
        db,
        data.nombre,
        data.email,
        data.password,
        data.nombre_comercio,
    )

@router.post("/login", response_model=TokenResponse)
def login(data: UsuarioLogin, db=Depends(get_db)):
    return auth_service.login_usuario(db, data.email, data.password)


@router.get("/me", response_model=UsuarioOut)
def me(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        usuario_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido")

    usuario = auth_repo.obtener_usuario_por_id(db, usuario_id)

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    return usuario

@router.post("/refresh")
def refresh(data: RefreshRequest, db=Depends(get_db)):
    try:
        return auth_service.refresh_access_token(db, data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
def logout(data: RefreshRequest, db=Depends(get_db)):
    auth_service.logout(db, data.refresh_token)
    return {"message": "Logout exitoso"}