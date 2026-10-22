import html
import json
import os
import re
from datetime import datetime, timezone
from typing import Dict, Optional

from fastapi import Request

SITE_NAME = "Tinhat"
OG_IMAGE_PATH = "/og-image.png"
OG_IMAGE_ALT = "Tinhat — A secret that deletes itself"

DEFAULT_DESCRIPTION = (
    "Send passwords, API keys and private notes through a one-time link. "
    "The secret is deleted after the first view or when the timer runs out. "
    "No accounts, no logs."
)

ROUTES: Dict[str, Dict] = {
    "/": {
        "title": "Tinhat — Share secrets that delete themselves",
        "description": DEFAULT_DESCRIPTION,
        "canonical": "/",
        "index": True,
        "sitemap": {"changefreq": "monthly", "priority": "1.0"},
    },
    "/privacy": {
        "title": "Privacy Policy — Tinhat",
        "description": (
            "Tinhat needs no email, password or registration. Secrets live in memory "
            "only and are purged after one view or when they expire."
        ),
        "canonical": "/privacy",
        "index": True,
        "sitemap": {"changefreq": "yearly", "priority": "0.3"},
    },
    "/terms": {
        "title": "Terms of Service — Tinhat",
        "description": (
            "Acceptable use, availability and liability terms for Tinhat, "
            "the one-time secret sharing service."
        ),
        "canonical": "/terms",
        "index": True,
        "sitemap": {"changefreq": "yearly", "priority": "0.3"},
    },
    "/accept": {
        "title": "Open a one-time secret — Tinhat",
        "description": "One-time secret. Opens once, then it’s gone.",
        "canonical": None,
        "index": False,
    },
    "/link-not-found": {
        "title": "This secret has burned — Tinhat",
        "description": "This link has expired or was already opened.",
        "canonical": None,
        "index": False,
    },
}

# Client-side aliases. Permanent redirects keep a single canonical URL per page.
REDIRECTS = {
    "/compose": "/",
    "/index.html": "/",
}
# Alias that is still served (noindex), kept for old links.
ROUTE_ALIASES = {"/expired": "/link-not-found"}

NOT_FOUND_META = {
    "title": "Page not found — Tinhat",
    "description": "This page does not exist.",
    "canonical": None,
    "index": False,
}

NOINDEX_PREFIXES = ("/accept", "/link-not-found", "/expired", "/api/")

_SEO_BLOCK_RE = re.compile(r"<!--seo:start-->.*?<!--seo:end-->", re.DOTALL)
_VALID_HOST_RE = re.compile(r"^[A-Za-z0-9.-]+(?::\d{1,5})?$")


def get_site_url(request: Request, trust_proxy: bool = False) -> str:
    """Public origin used for canonical/OG URLs. Prefer the SITE_URL env var in production."""
    configured = os.environ.get("SITE_URL", "").strip().rstrip("/")
    if configured:
        return configured

    scheme = request.url.scheme
    host = request.headers.get("host") or request.url.netloc
    if trust_proxy:
        scheme = request.headers.get("x-forwarded-proto", scheme).split(",")[0].strip()
        host = request.headers.get("x-forwarded-host", host).split(",")[0].strip()

    if scheme not in ("http", "https"):
        scheme = "http"
    if not host or not _VALID_HOST_RE.match(host):
        host = "localhost:8000"

    return f"{scheme}://{host}".rstrip("/")


def resolve_route(path: str) -> Optional[Dict]:
    """Return SEO metadata for a known route, or None for unknown paths (404)."""
    key = ROUTE_ALIASES.get(path, path)
    return ROUTES.get(key)


def is_noindex_path(path: str) -> bool:
    return path.startswith(NOINDEX_PREFIXES)


def _json_ld(site_url: str) -> str:
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{site_url}/#website",
                "url": f"{site_url}/",
                "name": SITE_NAME,
                "description": DEFAULT_DESCRIPTION,
                "inLanguage": "en",
            },
            {
                "@type": "WebApplication",
                "@id": f"{site_url}/#app",
                "name": SITE_NAME,
                "url": f"{site_url}/",
                "description": DEFAULT_DESCRIPTION,
                "applicationCategory": "SecurityApplication",
                "operatingSystem": "Any",
                "browserRequirements": "Requires JavaScript",
                "image": f"{site_url}{OG_IMAGE_PATH}",
                "isAccessibleForFree": True,
                "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
                "featureList": [
                    "One-time links that burn on first view",
                    "Auto-delete timer from 5 minutes to 24 hours",
                    "QR code for sharing to mobile",
                    "No accounts or registration",
                ],
            },
        ],
    }
    # "</" must never appear inside an inline <script> block
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


def render_seo_block(meta: Dict, site_url: str, is_home: bool = False) -> str:
    esc = lambda value: html.escape(value, quote=True)  # noqa: E731
    robots = (
        "index,follow,max-image-preview:large"
        if meta["index"]
        else "noindex,nofollow,noarchive"
    )
    canonical = f"{site_url}{meta['canonical']}" if meta["canonical"] else None
    image = f"{site_url}{OG_IMAGE_PATH}"

    lines = [
        "<!--seo:start-->",
        f"<title>{esc(meta['title'])}</title>",
        f'<meta name="description" content="{esc(meta["description"])}" />',
        f'<meta name="robots" content="{robots}" />',
    ]
    if canonical:
        lines.append(f'<link rel="canonical" href="{esc(canonical)}" />')
    lines += [
        '<meta property="og:type" content="website" />',
        f'<meta property="og:site_name" content="{SITE_NAME}" />',
        f'<meta property="og:title" content="{esc(meta["title"])}" />',
        f'<meta property="og:description" content="{esc(meta["description"])}" />',
        f'<meta property="og:image" content="{esc(image)}" />',
        '<meta property="og:image:width" content="1200" />',
        '<meta property="og:image:height" content="630" />',
        f'<meta property="og:image:alt" content="{esc(OG_IMAGE_ALT)}" />',
        '<meta property="og:locale" content="en_US" />',
    ]
    if canonical:
        lines.append(f'<meta property="og:url" content="{esc(canonical)}" />')
    lines += [
        '<meta name="twitter:card" content="summary_large_image" />',
        f'<meta name="twitter:title" content="{esc(meta["title"])}" />',
        f'<meta name="twitter:description" content="{esc(meta["description"])}" />',
        f'<meta name="twitter:image" content="{esc(image)}" />',
        f'<meta name="twitter:image:alt" content="{esc(OG_IMAGE_ALT)}" />',
    ]
    if is_home:
        lines.append(f'<script type="application/ld+json">{_json_ld(site_url)}</script>')
    lines.append("<!--seo:end-->")
    return "\n    ".join(lines)


def inject_seo(index_html: str, meta: Dict, site_url: str, is_home: bool = False) -> str:
    block = render_seo_block(meta, site_url, is_home)
    # Callable replacement so backslashes in the block are never treated as regex escapes
    return _SEO_BLOCK_RE.sub(lambda _m: block, index_html, count=1)


def render_robots(site_url: str) -> str:
    return "\n".join(
        [
            "User-agent: *",
            "Allow: /",
            "Disallow: /accept",
            "Disallow: /link-not-found",
            "Disallow: /expired",
            "Disallow: /api/",
            "",
            f"Sitemap: {site_url}/sitemap.xml",
            "",
        ]
    )


def render_sitemap(site_url: str, lastmod: Optional[float] = None) -> str:
    stamp = (
        datetime.fromtimestamp(lastmod, tz=timezone.utc).strftime("%Y-%m-%d")
        if lastmod
        else None
    )
    urls = []
    for path, meta in ROUTES.items():
        if not meta.get("index"):
            continue
        cfg = meta.get("sitemap", {})
        entry = [f"    <loc>{html.escape(site_url + path)}</loc>"]
        if stamp:
            entry.append(f"    <lastmod>{stamp}</lastmod>")
        if cfg.get("changefreq"):
            entry.append(f"    <changefreq>{cfg['changefreq']}</changefreq>")
        if cfg.get("priority"):
            entry.append(f"    <priority>{cfg['priority']}</priority>")
        urls.append("  <url>\n" + "\n".join(entry) + "\n  </url>")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )

