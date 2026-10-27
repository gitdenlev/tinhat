const API_BASE = '/api';

// The server is the only source of truth for quota. This object is just a
// placeholder shown until the first /api/quota response arrives.
const DEFAULT_QUOTA = Object.freeze({
  limit: 20,
  used: 0,
  remaining: 20,
  reset_in_seconds: 0
});

export function getDefaultQuota() {
  return { ...DEFAULT_QUOTA };
}

let cachedDeviceToken = null;

async function sha256Hex(input) {
  if (typeof crypto !== 'undefined' && crypto.subtle) {
    const data = new TextEncoder().encode(input);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hashBuffer), (b) =>
      b.toString(16).padStart(2, '0')
    ).join('');
  }
  let h1 = 0xdeadbeef ^ input.length;
  let h2 = 0x41c6ce57 ^ input.length;
  for (let i = 0; i < input.length; i++) {
    const ch = input.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return (h2 >>> 0).toString(16).padStart(8, '0') + (h1 >>> 0).toString(16).padStart(8, '0') + '00000000';
}

async function getDeviceToken() {
  if (cachedDeviceToken) return cachedDeviceToken;
  if (typeof window === 'undefined') return 'server';

  let gpuInfo = '';
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (gl) {
      const dbg = gl.getExtension('WEBGL_debug_renderer_info');
      const vendor = dbg ? gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR);
      const renderer = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
      gpuInfo = `${vendor || ''}|${renderer || ''}`;
    }
  } catch (_) {}

  const nav = typeof navigator !== 'undefined' ? navigator : {};
  const scr = typeof screen !== 'undefined' ? screen : {};
  const tz = typeof Intl !== 'undefined'
    ? Intl.DateTimeFormat().resolvedOptions().timeZone || ''
    : '';

  const rawSignals = [
    gpuInfo,
    `${scr.width || 0}x${scr.height || 0}x${scr.colorDepth || 0}`,
    `${window.devicePixelRatio || 1}`,
    `${nav.hardwareConcurrency || 0}`,
    `${nav.deviceMemory || 0}`,
    `${nav.maxTouchPoints || 0}`,
    `${nav.platform || ''}`,
    tz
  ].join('::');

  cachedDeviceToken = await sha256Hex(`tinhat-v1::${rawSignals}`);
  return cachedDeviceToken;
}

/**
 * Fetch the authoritative quota from the server.
 *
 * There is deliberately no localStorage/IndexedDB fallback counter: the client
 * cannot be trusted to enforce a limit, and persisting a counter there only
 * creates a false sense of security (and a counter the user can simply erase).
 * If the server is unreachable we show the default allowance; the actual
 * POST /api/secrets call is still rejected server-side when the quota is gone.
 */
export async function fetchDailyQuota() {
  try {
    const deviceToken = await getDeviceToken();
    const res = await fetch(`${API_BASE}/quota`, {
      credentials: 'same-origin',
      headers: { 'X-Device-Token': deviceToken }
    });
    if (res.ok) {
      const data = await res.json();
      if (typeof data?.remaining === 'number') {
        return data;
      }
    }
  } catch (_) {}
  return getDefaultQuota();
}

export async function createSecret(data) {
  const deviceToken = await getDeviceToken();
  const res = await fetch(`${API_BASE}/secrets`, {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-Device-Token': deviceToken
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    if (res.status === 502 || res.status === 503 || res.status === 504) {
      const err = new Error('Backend server is unreachable (502 Bad Gateway). Please make sure the FastAPI backend is running on port 8000.');
      err.status = res.status;
      throw err;
    }
    const errorData = await res.json().catch(() => ({}));
    const detail = errorData.detail;
    const message =
      (typeof detail === 'object' && detail?.message) ||
      (typeof detail === 'string' && detail) ||
      'Failed to create secret';
    const err = new Error(message);
    err.status = res.status;
    if (typeof detail === 'object' && detail?.quota) {
      err.quota = detail.quota;
    }
    throw err;
  }
  return res.json();
}

export async function getSecret(secretId) {
  const res = await fetch(`${API_BASE}/secrets/${encodeURIComponent(secretId)}`);
  if (!res.ok) {
    if (res.status === 502 || res.status === 503 || res.status === 504) {
      const err = new Error('Backend server is unreachable (502 Bad Gateway). Please make sure the FastAPI backend is running on port 8000.');
      err.status = res.status;
      throw err;
    }
    const errorData = await res.json().catch(() => ({}));
    const err = new Error(errorData.detail || 'Secret not found or expired');
    err.status = res.status;
    throw err;
  }
  return res.json();
}

export async function acceptSecret(secretId) {
  const res = await fetch(`${API_BASE}/secrets/${encodeURIComponent(secretId)}/accept`, {
    method: 'POST'
  });
  if (!res.ok) {
    if (res.status === 502 || res.status === 503 || res.status === 504) {
      const err = new Error('Backend server is unreachable (502 Bad Gateway). Please make sure the FastAPI backend is running on port 8000.');
      err.status = res.status;
      throw err;
    }
    const errorData = await res.json().catch(() => ({}));
    const err = new Error(errorData.detail || 'Failed to accept secret');
    err.status = res.status;
    throw err;
  }
  return res.json();
}
