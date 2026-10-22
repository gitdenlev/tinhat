import os
from typing import Any, Dict

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
)
from fastapi.staticfiles import StaticFiles

from .. import seo
from ..config import DIST_DIR, INDEX_HTML_PATH, PUBLIC_DIR, TRUST_PROXY

router = APIRouter()

_index_cache: Dict[str, Any] = {"mtime": None, "html": ""}


class ImmutableStaticFiles(StaticFiles):
    """Vite emits content-hashed filenames in /assets, so they can be cached forever."""

    async def get_response(self, path, scope):
        response = await super().get_response(path, scope)
        if response.status_code == 200:
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


def mount_static(app: FastAPI) -> None:
    """Mount /public and the hashed /assets bundle (must be called before the SPA router)."""
    if os.path.exists(PUBLIC_DIR):
        app.mount("/public", StaticFiles(directory=PUBLIC_DIR), name="public")

    assets_dir = os.path.join(DIST_DIR, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", ImmutableStaticFiles(directory=assets_dir), name="assets")


def _load_index_html() -> str | None:
    """Read dist/index.html, re-reading only when the build output changes."""
    try:
        mtime = os.path.getmtime(INDEX_HTML_PATH)
    except OSError:
        return None
    if _index_cache["mtime"] != mtime:
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as fh:
            _index_cache["html"] = fh.read()
        _index_cache["mtime"] = mtime
    return _index_cache["html"]


def _site_url(request: Request) -> str:
    return seo.get_site_url(request, trust_proxy=TRUST_PROXY)


@router.get("/robots.txt", include_in_schema=False)
async def robots_txt(request: Request):
    return PlainTextResponse(
        seo.render_robots(_site_url(request)),
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap_xml(request: Request):
    try:
        lastmod = os.path.getmtime(INDEX_HTML_PATH)
    except OSError:
        lastmod = None
    return Response(
        content=seo.render_sitemap(_site_url(request), lastmod),
        media_type="application/xml",
        headers={"Cache-Control": "public, max-age=3600"},
    )


@router.api_route("/{full_path:path}", methods=["GET", "HEAD"])
async def serve_spa(full_path: str, request: Request):
    """Serve Svelte SPA for any client route or direct file, with per-route SEO tags."""
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API route not found")

    if full_path:
        for base_dir in (DIST_DIR, PUBLIC_DIR):
            candidate = os.path.abspath(os.path.join(base_dir, full_path))
            if candidate.startswith(base_dir + os.sep) and os.path.isfile(candidate):
                if os.path.basename(candidate) == "index.html":
                    break  # rendered below with SEO tags
                return FileResponse(
                    candidate, headers={"Cache-Control": "public, max-age=86400"}
                )

    path = "/" + full_path
    query = f"?{request.url.query}" if request.url.query else ""

    # One canonical URL per page: /compose -> /, /privacy/ -> /privacy
    if path in seo.REDIRECTS:
        return RedirectResponse(seo.REDIRECTS[path] + query, status_code=301)
    if len(path) > 1 and path.endswith("/"):
        return RedirectResponse(path.rstrip("/") + query, status_code=301)

    index_html = _load_index_html()
    if index_html is None:
        return JSONResponse(
            status_code=200,
            content={"message": "Frontend not built yet. Run 'npm run build' first."},
        )

    meta = seo.resolve_route(path)
    status_code = 200
    if meta is None:
        # Unknown URL: real 404 status so search engines don't index soft-404 pages
        meta = seo.NOT_FOUND_META
        status_code = 404

    page = seo.inject_seo(index_html, meta, _site_url(request), is_home=path == "/")
    headers = {"Cache-Control": "no-cache"}
    if not meta["index"]:
        headers["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return HTMLResponse(page, status_code=status_code, headers=headers)

