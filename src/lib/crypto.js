const E2EE_PREFIX = 'e2ee:v1:';
const IV_BYTE_LENGTH = 12;   // 96-bit IV recommended by NIST SP 800-38D for AES-GCM
const KEY_BYTE_LENGTH = 32;  // 256-bit AES key

function bytesToBase64Url(bytes) {
  let binary = '';
  for (let i = 0; i < bytes.length; i++) {
    binary += String.fromCharCode(bytes[i]);
  }
  return btoa(binary)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/g, '');
}

function base64UrlToBytes(b64url) {
  const padded = b64url
    .replace(/-/g, '+')
    .replace(/_/g, '/')
    .padEnd(Math.ceil(b64url.length / 4) * 4, '=');
  const binary = atob(padded);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return bytes;
}

export function isEncryptedPayload(payload) {
  return typeof payload === 'string' && payload.startsWith(E2EE_PREFIX);
}

export function hasValidDecryptionKey(keyB64) {
  const cleanKey = (keyB64 || '').replace(/^#/, '').trim();
  if (!cleanKey) return false;
  try {
    return base64UrlToBytes(cleanKey).length === KEY_BYTE_LENGTH;
  } catch (_) {
    return false;
  }
}

/**
 * Encrypts plaintext on the client using AES-256-GCM.
 * Returns { payload, key } where `key` is placed only in the URL #fragment (never sent to server).
 */
export async function encryptSecretClient(plaintext) {
  if (typeof crypto === 'undefined' || !crypto.subtle) {
    throw new Error('Web Crypto API is unavailable. Please use HTTPS or localhost.');
  }

  const rawKey = crypto.getRandomValues(new Uint8Array(KEY_BYTE_LENGTH));
  const iv = crypto.getRandomValues(new Uint8Array(IV_BYTE_LENGTH));

  const cryptoKey = await crypto.subtle.importKey(
    'raw',
    rawKey,
    { name: 'AES-GCM' },
    false,
    ['encrypt']
  );

  const encoded = new TextEncoder().encode(plaintext);
  const cipherBuffer = await crypto.subtle.encrypt(
    { name: 'AES-GCM', iv },
    cryptoKey,
    encoded
  );

  const ivB64 = bytesToBase64Url(iv);
  const ctB64 = bytesToBase64Url(new Uint8Array(cipherBuffer));
  const keyB64 = bytesToBase64Url(rawKey);

  return {
    payload: `${E2EE_PREFIX}${ivB64}.${ctB64}`,
    key: keyB64
  };
}

/**
 * Decrypts an `e2ee:v1:<iv>.<ciphertext>` payload using the Base64URL key from the URL #fragment.
 * Plaintext secrets created directly via the REST API (without the E2EE prefix) pass through unchanged.
 */
export async function decryptSecretClient(payload, keyB64) {
  if (!isEncryptedPayload(payload)) {
    return payload;
  }

  const cleanKey = (keyB64 || '').replace(/^#/, '').trim();
  if (!cleanKey) {
    throw new Error('Decryption key is missing from the link.');
  }

  if (typeof crypto === 'undefined' || !crypto.subtle) {
    throw new Error('Web Crypto API is unavailable. Please use HTTPS or localhost.');
  }

  const body = payload.slice(E2EE_PREFIX.length);
  const dotIdx = body.indexOf('.');
  if (dotIdx <= 0) {
    throw new Error('Malformed encrypted payload.');
  }

  let iv;
  let ciphertext;
  let rawKey;
  try {
    iv = base64UrlToBytes(body.slice(0, dotIdx));
    ciphertext = base64UrlToBytes(body.slice(dotIdx + 1));
    rawKey = base64UrlToBytes(cleanKey);
  } catch (_) {
    throw new Error('Invalid decryption key or corrupted ciphertext.');
  }

  if (iv.length !== IV_BYTE_LENGTH || rawKey.length !== KEY_BYTE_LENGTH) {
    throw new Error('Invalid decryption key length.');
  }

  try {
    const cryptoKey = await crypto.subtle.importKey(
      'raw',
      rawKey,
      { name: 'AES-GCM' },
      false,
      ['decrypt']
    );

    const plainBuffer = await crypto.subtle.decrypt(
      { name: 'AES-GCM', iv },
      cryptoKey,
      ciphertext
    );

    return new TextDecoder().decode(plainBuffer);
  } catch (_) {
    throw new Error('Failed to decrypt secret. The link key may be invalid or incomplete.');
  }
}

