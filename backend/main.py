# app/main.py
from fastapi import FastAPI
from backend.routers.webhook import router as webhook_router
from backend.routers.comercios import router as comercios_router
from backend.database import init_db
from backend.routers.pagos import router as pagos_router
from fastapi.middleware.cors import CORSMiddleware
from backend.routers.auth import router as auth_router

app = FastAPI()

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # después lo hacemos más seguro
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(pagos_router)
app.include_router(comercios_router)
app.include_router(webhook_router)
app.include_router(auth_router)