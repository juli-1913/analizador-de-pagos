from fastapi import APIRouter, Depends
from backend.database import get_db
from backend.schemas.clase_comercios import Comercio, ComercioCreate
from backend.services import comercios_service as cs
from backend.core.security import get_current_user

router = APIRouter(prefix="/comercios", tags=["comercios"])


@router.post("", response_model=Comercio, status_code=201)
def crear_comercio(comercio: ComercioCreate, db=Depends(get_db)):
    return cs.crear_comercio(
        db,
        comercio.nombre,
        comercio.email
    )


@router.get("/mi-comercio")
def obtener_mi_comercio(user=Depends(get_current_user)):
    return user