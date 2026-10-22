// Client-side SEO: keeps <head> in sync with the current SPA route.
// The server (main.py) renders the same values into the initial HTML for crawlers
// and link previews, so keep both route tables aligned.

export const SITE_NAME = 'Tinhat';
const OG_IMAGE_PATH = '/og-image.png';

const DEFAULT_DESCRIPTION =
  'Send passwords, API keys and private notes through a one-time link. The secret is deleted after the first view or when the timer runs out. No accounts, no logs.';

const ROUTES = {
  '/': {
    title: 'Tinhat — Share secrets that delete themselves',
    description: DEFAULT_DESCRIPTION,
    canonical: '/',
    index: true
  },
  '/privacy': {
    title: 'Privacy Policy — Tinhat',
    description:
      'Tinhat needs no email, password or registration. Secrets live in memory only and are purged after one view or when they expire.',
    canonical: '/privacy',
    index: true
  },
  '/terms': {
    title: 'Terms of Service — Tinhat',
    description:
      'Acceptable use, availability and liability terms for Tinhat, the one-time secret sharing service.',
    canonical: '/terms',
    index: true
  },
  '/accept': {
    title: 'Open a one-time secret — Tinhat',
    description: 'One-time secret. Opens once, then it’s gone.',
    canonical: null,
    index: false
  },
  '/link-not-found': {
    title: 'This secret has burned — Tinhat',
    description: 'This link has expired or was already opened.',
    canonical: null,
    index: false
  }
};

const ALIASES = {
  '': '/',
  '/compose': '/',
  '/expired': '/link-not-found'
};

const NOT_FOUND = {
  title: 'Page not found — Tinhat',
  description: 'This page does not exist.',
  canonical: null,
  index: false
};

export function resolveRouteMeta(path) {
  const key = ALIASES[path] ?? path;
  return ROUTES[key] ?? NOT_FOUND;
}

function upsertMeta(attr, name, content) {
  let el = document.head.querySelector(`meta[${attr}="${name}"]`);
  if (!el) {
    el = document.createElement('meta');
    el.setAttribute(attr, name);
    document.head.appendChild(el);
  }
  el.setAttribute('content', content);
}

function upsertCanonical(href) {
  let el = document.head.querySelector('link[rel="canonical"]');
  if (!href) {
    el?.remove();
    return;
  }
  if (!el) {
    el = document.createElement('link');
    el.setAttribute('rel', 'canonical');
    document.head.appendChild(el);
  }
  el.setAttribute('href', href);
}

export function applySeo(path) {
  if (typeof document === 'undefined') return;

  const meta = resolveRouteMeta(path);
  const origin = window.location.origin;
  const canonical = meta.canonical ? origin + meta.canonical : null;
  const robots = meta.index
    ? 'index,follow,max-image-preview:large'
    : 'noindex,nofollow,noarchive';

  document.title = meta.title;
  upsertMeta('name', 'description', meta.description);
  upsertMeta('name', 'robots', robots);
  upsertCanonical(canonical);

  upsertMeta('property', 'og:type', 'website');
  upsertMeta('property', 'og:site_name', SITE_NAME);
  upsertMeta('property', 'og:title', meta.title);
  upsertMeta('property', 'og:description', meta.description);
  upsertMeta('property', 'og:image', origin + OG_IMAGE_PATH);
  upsertMeta('property', 'og:image:width', '1200');
  upsertMeta('property', 'og:image:height', '630');
  upsertMeta('property', 'og:image:alt', 'Tinhat — A secret that deletes itself');
  if (canonical) upsertMeta('property', 'og:url', canonical);

  upsertMeta('name', 'twitter:card', 'summary_large_image');
  upsertMeta('name', 'twitter:title', meta.title);
  upsertMeta('name', 'twitter:description', meta.description);
  upsertMeta('name', 'twitter:image', origin + OG_IMAGE_PATH);
}

