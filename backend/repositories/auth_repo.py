from datetime import datetime
import secrets


def crear_usuario(db, nombre, email, password_hash, comercio_id):
    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO usuarios (nombre, email, password_hash, comercio_id)
            VALUES (%s, %s, %s, %s)
            RETURNING id, nombre, email, comercio_id
            """,
            (nombre, email, password_hash, comercio_id),
        )
        fila = cursor.fetchone()

    db.commit()
    return fila


def obtener_usuario_por_email(db, email):
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM usuarios
            WHERE email = %s
            """,
            (email,),
        )
        fila = cursor.fetchone()

    return fila


def obtener_usuario_por_id(db, usuario_id):
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, nombre, email, comercio_id
            FROM usuarios
            WHERE id = %s
            """,
            (usuario_id,),
        )
        fila = cursor.fetchone()

    return fila


def crear_refresh_token(db, usuario_id, token, expires_at):
    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO refresh_tokens (usuario_id, token, expires_at)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (usuario_id, token, expires_at),
        )
        fila = cursor.fetchone()

    db.commit()
    return fila


def obtener_refresh_token(db, token):
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM refresh_tokens
            WHERE token = %s
            """,
            (token,),
        )
        fila = cursor.fetchone()

    return fila


def revocar_refresh_token(db, token):
    with db.cursor() as cursor:
        cursor.execute(
            """
            UPDATE refresh_tokens
            SET revoked = TRUE
            WHERE token = %s
            """,
            (token,),
        )

    db.commit()


def crear_comercio_para_usuario(db, nombre_comercio, email):
    api_key = secrets.token_hex(16)

    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO comercios (nombre, email, api_key)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (nombre_comercio, email, api_key),
        )
        fila = cursor.fetchone()

    db.commit()
    return fila