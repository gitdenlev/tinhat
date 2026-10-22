"""HTTP middleware: CORS, gzip and privacy/security headers."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from . import seo
from .config import CORS_ORIGINS

CSP_POLICY = (
    "default-src 'self'; "
    "script-src 'self'; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com data:; "
    "img-src 'self' data: blob:; "
    "connect-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'none'"
)


async def seo_and_security_headers(request: Request, call_next):
    """Privacy/SEO headers: keep secret URLs out of indexes and referrers, never cache API data."""
    response = await call_next(request)
    path = request.url.path

    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Content-Security-Policy", CSP_POLICY)
    response.headers.setdefault(
        "Permissions-Policy", "camera=(), microphone=(), geolocation=(), interest-cohort=()"
    )

    if seo.is_noindex_path(path):
        response.headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        # Secret IDs live in the URL, so never leak them via the Referer header
        response.headers["Referrer-Policy"] = "no-referrer"
    else:
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")

    if path.startswith("/api/") or path.startswith("/accept"):
        response.headers["Cache-Control"] = "no-store"

    return response


def register_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=False,
        allow_methods=["GET", "POST", "HEAD", "OPTIONS"],
        allow_headers=["Content-Type", "X-Device-Token"],
    )
    app.add_middleware(GZipMiddleware, minimum_size=1024)
    app.middleware("http")(seo_and_security_headers)
