<script>
  import DocsPage from '../components/DocsPage.svelte';
</script>

<DocsPage title="Privacy Policy">
  <h3>Zero Knowledge & Zero Accounts</h3>
  <p>
    Tinhat requires no email, no password, no nicknames, and no registration. All secret links are anonymous.
  </p>

  <h3>Ephemeral Encrypted Storage &amp; Short Default Lifetime</h3>
  <p>
    Messages are encrypted in your browser before upload; the decryption key stays in the link and is never sent to us. The encrypted data is kept in memory or in a managed Redis database (Upstash) only for the default lifetime (1 hour) or the custom duration you choose. Once viewed or expired, secrets are purged permanently with zero logs retained.
  </p>

  <h3>No Link Revocation</h3>
  <p>
    Links cannot be revoked. If you sent a link to the wrong person, it works until it’s opened or expires.
  </p>

  <h3>No Tracking</h3>
  <p>
    We do not use advertising cookies, third-party analytics trackers, or personal telemetry.
  </p>

  <h3>Anonymous Abuse Prevention</h3>
  <p>
    To protect the service from spam, we enforce a daily generation limit using ephemeral, one-way salted cryptographic hashes (<code>HMAC-SHA256</code>) kept strictly in memory. Raw IP addresses and raw device parameters are never stored, hashes are never associated with any secret message, and all rate-limit counters are automatically purged within 24 hours.
  </p>
  <p>
    We also set one first-party, HttpOnly cookie containing a random anonymous identifier. It is used only as a rate-limit bucket, is never linked to a secret, and expires after 24 hours. Clearing browser storage does not reset the limit; if the cookie is cleared too, the hashed IP-based bucket still applies.
  </p>
</DocsPage>
