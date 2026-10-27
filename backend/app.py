from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from .middleware import register_middleware
from .routes import api, spa
from .store import StoreUnavailable, store


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await store.close()


async def _store_unavailable_handler(request: Request, exc: StoreUnavailable) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={"detail": str(exc)},
        headers={"Retry-After": "5"},
    )


def create_app() -> FastAPI:
    app = FastAPI(
        title="Tinhat API",
        description="Share secrets that delete themselves — Powered by FastAPI + Svelte 5",
        version="2.2.0",
        lifespan=lifespan,
    )
    register_middleware(app)
    app.add_exception_handler(StoreUnavailable, _store_unavailable_handler)

    app.include_router(api.router)
    spa.mount_static(app)
    app.include_router(spa.router)
    return app
