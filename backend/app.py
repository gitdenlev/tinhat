from fastapi import FastAPI

from .middleware import register_middleware
from .routes import api, spa


def create_app() -> FastAPI:
    app = FastAPI(
        title="Tinhat API",
        description="Share secrets that delete themselves — Powered by FastAPI + Svelte 5",
        version="2.2.0",
    )
    register_middleware(app)

    app.include_router(api.router)
    spa.mount_static(app)
    app.include_router(spa.router)
    return app

