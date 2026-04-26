from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # entorno
    ENV: str = "development"

    # base de datos
    DATABASE_HOST: str
    DATABASE_NAME: str
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    WEBHOOK_URL: str
    # mercado pago
    MP_ACCESS_TOKEN: str
    MP_WEBHOOK_SECRET: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # configuracion de pydantic
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()