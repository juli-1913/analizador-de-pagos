def create_comercio(db, nombre, email, api_key):
    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO comercios (nombre, email, api_key)
            VALUES (%s, %s, %s)
            RETURNING *
            """,
            (nombre, email, api_key)
        )
        fila = cursor.fetchone()

    db.commit()
    return fila