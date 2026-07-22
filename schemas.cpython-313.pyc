from fastapi import APIRouter

from . import admin, auth, billing, dashboard, public, system, users, webhooks

api_router = APIRouter()
api_router.include_router(public.router)
api_router.include_router(auth.router)
api_router.include_router(billing.router)
api_router.include_router(dashboard.router)
api_router.include_router(admin.router)
api_router.include_router(system.router)
api_router.include_router(users.router)
api_router.include_router(webhooks.router)
