import psycopg
from psycopg.rows import dict_row
from backend.core.config import settings


def get_connection():
    return psycopg.connect(
        host=settings.DATABASE_HOST,
        dbname=settings.DATABASE_NAME,
        user=settings.DATABASE_USER,
        password=settings.DATABASE_PASSWORD,
        row_factory=dict_row
    )

def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS comercios (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    api_key TEXT UNIQUE NOT NULL,
                    fecha_creacion TIMESTAMP DEFAULT NOW()
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pagos (
                    id SERIAL PRIMARY KEY,
                    monto INTEGER NOT NULL,
                    fecha DATE NOT NULL,
                    estado VARCHAR(50) NOT NULL
                )
            """)

            cursor.execute("""
                ALTER TABLE pagos
                ADD COLUMN IF NOT EXISTS comercio_id INTEGER REFERENCES comercios(id)
            """)

            cursor.execute("""
                ALTER TABLE pagos
                ADD COLUMN IF NOT EXISTS mp_preference_id TEXT
            """)

            cursor.execute("""
                ALTER TABLE pagos
                ADD COLUMN IF NOT EXISTS mp_init_point TEXT
            """)

            cursor.execute("""
                ALTER TABLE pagos
                ADD COLUMN IF NOT EXISTS mp_payment_id TEXT
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    comercio_id INTEGER REFERENCES comercios(id),
                    fecha_creacion TIMESTAMP DEFAULT NOW()
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS refresh_tokens (
                    id SERIAL PRIMARY KEY,
                    usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW(),
                    revoked BOOLEAN DEFAULT FALSE
                )
            """)

        conn.commit()