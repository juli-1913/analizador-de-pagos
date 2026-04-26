import mercadopago

from backend.core.config import settings


sdk = mercadopago.SDK(settings.MP_ACCESS_TOKEN)


def crear_preference_pago(pago_id: int, monto: float):
    preference_data = {
        "items": [
            {
                "title": f"Pago #{pago_id}",
                "quantity": 1,
                "unit_price": monto,
                "currency_id": "ARS",
            }
        ],
        "external_reference": str(pago_id),
        "notification_url": settings.WEBHOOK_URL,
    }

    response = sdk.preference().create(preference_data)
    body = response["response"]

    return {
        "preference_id": body["id"],
        "init_point": body["init_point"],
    }