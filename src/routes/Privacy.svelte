<script>
  import DocsPage from '../components/DocsPage.svelte';
</script>

<DocsPage title="Privacy Policy">
  <h3>Zero Knowledge & Zero Accounts</h3>
  <p>
    Tinhat requires no email, no password, no nicknames, and no registration. All secret links are anonymous.
  </p>

  <h3>Ephemeral In-Memory Storage & Short Default Lifetime</h3>
  <p>
    All confidential messages are stored strictly in-memory with a short default lifetime (1 hour) or the custom duration you choose. Once viewed or expired, secrets are purged permanently with zero logs retained.
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
</DocsPage>
