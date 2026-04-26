from pydantic import BaseModel, EmailStr


class UsuarioRegistro(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    nombre_comercio: str


class UsuarioLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    comercio_id: int | None = None
    
class RefreshRequest(BaseModel):
    refresh_token: str