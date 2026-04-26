# app/services/pagos_service.py

from typing import Any, Optional
from datetime import date

from backend.repositories import pagos_repo as pr
from backend.services.mercadopago_service import crear_preference_pago

ESTADOS_PERMITIDOS = {"pendiente", "pagado","rechazado", "cancelado"}

ESTADOS_MP_A_INTERNOS = {
    "approved": "pagado",
    "pending": "pendiente",
    "rejected": "rechazado",
    "cancelled": "cancelado",
}

def mapear_estado_mp(status_mp: str) -> str:
    return ESTADOS_MP_A_INTERNOS.get(status_mp, "pendiente")

def _norm_estado(estado: str) -> str:
    return estado.strip().lower()


def listar_pagos(
    db,
    comercio_id: int,
    fecha: Optional[date],
    desde: Optional[date],
    hasta: Optional[date],
    monto_min: Optional[float],
    monto_max: Optional[float],
    estado: Optional[str],
):
    query_extra = ""
    params: list[Any] = []

    if fecha:
        query_extra += " AND fecha = %s"
        params.append(fecha)

    if desde:
        query_extra += " AND fecha >= %s"
        params.append(desde)

    if hasta:
        query_extra += " AND fecha <= %s"
        params.append(hasta)

    if monto_min is not None:
        query_extra += " AND monto >= %s"
        params.append(monto_min)

    if monto_max is not None:
        query_extra += " AND monto <= %s"
        params.append(monto_max)

    if estado:
        query_extra += " AND LOWER(estado) = %s"
        params.append(_norm_estado(estado))

    return pr.get_pagos_by_comercio(db, comercio_id, query_extra, tuple(params))


def obtener_pago(db, id: int, comercio_id: int) -> Optional[dict]:
    return pr.get_pago_by_id_and_comercio(db, id, comercio_id)


def actualizar_pago(
    db,
    id: int,
    comercio_id: int,
    monto: float,
    fecha: date,
    estado: str
) -> Optional[dict]:
    est = _norm_estado(estado)

    if est not in ESTADOS_PERMITIDOS:
        raise ValueError("Estado inválido. Usá: pendiente, pagado, rechazado, cancelado")

    return pr.update_pago_by_comercio(db, id, comercio_id, monto, fecha, est)


def eliminar_pago(db, id: int, comercio_id: int) -> bool:
    return pr.delete_pago_by_comercio(db, id, comercio_id)


def crear_pago(db, monto, fecha, estado, comercio_id):
    est = _norm_estado(estado)

    if est not in ESTADOS_PERMITIDOS:
        raise ValueError("Estado inválido. Usá: pendiente, pagado, rechazado, cancelado")
    
    print("1. Voy a crear pago en DB")
    nuevo_pago = pr.create_pago(db, monto, fecha, est, comercio_id)
    print("2. Pago creado en DB")

    pago_id = nuevo_pago["id"]
    print("3. Voy a crear preference en MP")
    

    mp_data = crear_preference_pago(pago_id, monto)
    print("4. Preference creada en MP", mp_data)

    print("5. Voy a guardar preference en DB")
    pr.guardar_preference_mp(
        db,
        pago_id,
        mp_data["preference_id"],
        mp_data["init_point"]
    )
    print("6. Preference guardada en DB")

    nuevo_pago["mp_preference_id"] = mp_data["preference_id"]
    nuevo_pago["mp_init_point"] = mp_data["init_point"]
    nuevo_pago["mp_payment_id"] = None

    print("7. Voy a devolver respuesta")
    return nuevo_pago