from __future__ import annotations

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, billing, games, invites, picks, system
from app.core.config import settings
from app.services.scheduler import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title=settings.app_name,
    version="3.2.0",
    description="EdgeBoard commercial MLB intelligence API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(picks.router, prefix="/api/v1")
app.include_router(games.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")
app.include_router(billing.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")
app.include_router(invites.router, prefix="/api/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": "edgeboard-api", "version": "3.2.0"}
