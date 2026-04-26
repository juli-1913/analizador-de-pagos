from fastapi import APIRouter, Request, Depends
from backend.database import get_db
from backend.core.config import settings
from backend.repositories import pagos_repo
from backend.services.pagos_service import mapear_estado_mp
import mercadopago
import hmac
import hashlib

router = APIRouter()

sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)

ESTADO_ORDEN = {
    "pendiente": 1,
    "pagado": 2,
    "rechazado": 2,
    "cancelado": 2,
}


def parsear_x_signature(x_signature: str):
    partes = x_signature.split(",")
    datos = {}

    for parte in partes:
        clave, valor = parte.split("=", 1)
        datos[clave.strip()] = valor.strip()

    return datos


@router.post("/webhooks/mercadopago")
async def webhook_mp(request: Request, db=Depends(get_db)):
    print("ENTRO AL WEBHOOK", flush=True)

    body = await request.json()
    print("Webhook recibido:", body, flush=True)

    x_signature = request.headers.get("x-signature")
    x_request_id = request.headers.get("x-request-id")

    print("x-signature:", x_signature, flush=True)
    print("x-request-id:", x_request_id, flush=True)

    # Solo procesamos webhooks del tipo payment con data.id
    if body.get("type") != "payment":
        print("⚠️ No es tipo payment", flush=True)
        return {"status": "ignored"}

    if "data" not in body or "id" not in body["data"]:
        print("⚠️ No tiene data.id", flush=True)
        return {"status": "ignored"}

    payment_id = body["data"]["id"]
    print("Payment ID:", payment_id, flush=True)

    # Validación de firma (modo desarrollo)
    if x_signature:
        firma = parsear_x_signature(x_signature)

        ts = firma.get("ts")
        v1 = firma.get("v1")

        print("ts:", ts, flush=True)
        print("v1:", v1, flush=True)

        if ts and v1 and x_request_id:
            message = f"id:{payment_id};request-id:{x_request_id};ts:{ts};"
            print("message:", message, flush=True)

            hash_calculado = hmac.new(
                settings.MP_WEBHOOK_SECRET.encode("utf-8"),
                message.encode("utf-8"),
                hashlib.sha256
            ).hexdigest()

            print("hash_calculado:", hash_calculado, flush=True)
            print("hash_recibido:", v1, flush=True)

            if hmac.compare_digest(hash_calculado, v1):
                print("✅ Firma válida", flush=True)
            else:
                print("⚠️ Firma no validada (modo desarrollo)", flush=True)
        else:
            print("⚠️ Firma incompleta (modo desarrollo)", flush=True)
    else:
        print("⚠️ No vino x-signature (modo desarrollo)", flush=True)

    payment_response = sdk.payment().get(payment_id)
    payment = payment_response["response"]

    status_mp = payment["status"]
    estado_interno = mapear_estado_mp(status_mp)

    print("Estado MP:", status_mp, flush=True)
    print("Estado interno:", estado_interno, flush=True)

    external_reference = payment.get("external_reference")

    if not external_reference:
        return {"status": "no_reference"}

    pago = pagos_repo.get_pago_by_external_reference(db, external_reference)

    if not pago:
        return {"status": "payment_not_found"}

    if pago["mp_payment_id"] == str(payment_id):
        return {"status": "already_processed"}

    estado_actual = pago["estado"]
    print("Estado actual DB:", estado_actual, flush=True)

    if ESTADO_ORDEN.get(estado_interno, 0) < ESTADO_ORDEN.get(estado_actual, 0):
        print("⚠️ Estado ignorado por retroceso", flush=True)
        return {"status": "ignored_state_regression"}

    print("Actualizando pago:", external_reference, flush=True)

    pagos_repo.actualizar_pago_mp(
        db,
        external_reference,
        payment_id,
        estado_interno
    )

    return {"status": "processed"}