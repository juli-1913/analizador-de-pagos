# app/repositories/pagos_repo.py

def create_pago(db, monto, fecha, estado, comercio_id):
    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO pagos (monto, fecha, estado, comercio_id)
            VALUES (%s, %s, %s, %s)
            RETURNING *
            """,
            (monto, fecha, estado, comercio_id)
        )
        fila = cursor.fetchone()

    db.commit()
    return fila

def guardar_preference_mp(conn, pago_id: int, preference_id: str, init_point: str):
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE pagos
            SET mp_preference_id = %s,
                mp_init_point = %s
            WHERE id = %s
        """, (preference_id, init_point, pago_id))

    conn.commit()
    
def actualizar_pago_mp(conn, pago_id, payment_id, status):

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE pagos
            SET mp_payment_id = %s,
                estado = %s
            WHERE id = %s
            """,
            (payment_id, status, pago_id),
        )

    conn.commit()
    
def get_pago_by_external_reference(db, external_reference):
    with db.cursor() as cursor:
        cursor.execute(
            "SELECT * FROM pagos WHERE id = %s",
            (external_reference,)
        )
        fila = cursor.fetchone()

    return fila

def get_pagos_by_comercio(db, comercio_id, query_extra="", parametros_extra=()):
    query = f"""
        SELECT * FROM pagos
        WHERE comercio_id = %s
        {query_extra}
        ORDER BY id
    """

    parametros = (comercio_id, *parametros_extra)

    with db.cursor() as cursor:
        cursor.execute(query, parametros)
        filas = cursor.fetchall()

    return filas

def get_pago_by_id_and_comercio(db, id, comercio_id):
    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT * FROM pagos
            WHERE id = %s AND comercio_id = %s
            """,
            (id, comercio_id)
        )
        fila = cursor.fetchone()

    return fila if fila else None

def update_pago_by_comercio(db, id, comercio_id, monto, fecha, estado):
    with db.cursor() as cursor:
        cursor.execute(
            """
            UPDATE pagos
            SET monto = %s, fecha = %s, estado = %s
            WHERE id = %s AND comercio_id = %s
            RETURNING *
            """,
            (monto, fecha, estado, id, comercio_id),
        )
        fila = cursor.fetchone()

    db.commit()
    return fila if fila else None

def delete_pago_by_comercio(db, id, comercio_id):
    with db.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM pagos
            WHERE id = %s AND comercio_id = %s
            RETURNING id
            """,
            (id, comercio_id)
        )
        eliminado = cursor.fetchone()

    db.commit()
    return eliminado is not None