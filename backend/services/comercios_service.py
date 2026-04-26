import secrets
from backend.repositories import comercios_repo as cr


def crear_comercio(db, nombre, email):
    api_key = secrets.token_hex(16)

    return cr.create_comercio(
        db,
        nombre,
        email,
        api_key
    )