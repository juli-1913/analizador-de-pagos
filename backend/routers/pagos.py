from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from datetime import date

from backend.core.security import get_current_user
from backend.database import get_db
from backend.schemas.clase_pagos import Pago, PagoCreate, PagoUpdate
from backend.services import pagos_service as ps

router = APIRouter(prefix="/pagos", tags=["pagos"])


@router.get("", response_model=list[Pago])
def obtener_pagos(
    fecha: Optional[date] = None,
    desde: Optional[date] = None,
    hasta: Optional[date] = None,
    monto_min: Optional[float] = None,
    monto_max: Optional[float] = None,
    estado: Optional[str] = None,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    return ps.listar_pagos(
        db,
        user["comercio_id"],
        fecha,
        desde,
        hasta,
        monto_min,
        monto_max,
        estado
    )


@router.get("/{id}", response_model=Pago)
def obtener_pago(
    id: int,
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    pago = ps.obtener_pago(db, id, user["comercio_id"])

    if pago is None:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    return pago


@router.post("", response_model=Pago, status_code=201)
def crear_pago(
    pago: PagoCreate,
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        return ps.crear_pago(
            db,
            pago.monto,
            pago.fecha,
            pago.estado,
            user["comercio_id"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{id}", response_model=Pago)
def actualizar_pago(
    id: int,
    pago: PagoUpdate,
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        pago_actualizado = ps.actualizar_pago(
            db,
            id,
            user["comercio_id"],
            pago.monto,
            pago.fecha,
            pago.estado
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if pago_actualizado is None:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    return pago_actualizado


@router.delete("/{id}", status_code=204)
def eliminar_pago(
    id: int,
    user=Depends(get_current_user),
    db=Depends(get_db)
):
    eliminado = ps.eliminar_pago(db, id, user["comercio_id"])

    if not eliminado:
        raise HTTPException(status_code=404, detail="Pago no encontrado")

    return None