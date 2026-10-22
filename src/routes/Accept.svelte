<script>
  import LeftPanel from '../components/LeftPanel.svelte';
  import RevealPrompt from '../components/accept/RevealPrompt.svelte';
  import DecryptedSecret from '../components/accept/DecryptedSecret.svelte';
  import LinkNotFound from './LinkNotFound.svelte';
  import { router } from '../lib/router.svelte.js';
  import { getSecret, acceptSecret } from '../lib/api.js';
  import { decryptSecretClient, hasValidDecryptionKey } from '../lib/crypto.js';
  import { ACCEPT_PANEL } from '../lib/content.js';
  import { useCountdown } from '../composables/useCountdown.svelte.js';

  let secretId = $derived(router.searchParams.get('s') || '');
  let secretKey = $derived((router.hash || window.location.hash || '').replace(/^#/, ''));
  let requiresKey = $state(false);
  let isExpired = $state(false);
  let isDecrypting = $state(false);
  let decryptedData = $state(null);
  let errorMessage = $state('');

  let isAccepted = $derived(decryptedData !== null);

  const countdown = useCountdown({
    active: () => !isAccepted && !isExpired,
    onExpire: () => { isExpired = true; }
  });

  $effect(() => {
    if (secretId) {
      loadSecret(secretId);
    } else {
      isExpired = true;
    }
  });

  async function loadSecret(id) {
    try {
      const data = await getSecret(id);
      if (data && typeof data.timeout_seconds === 'number') {
        requiresKey = Boolean(data.encrypted);
        countdown.seconds = data.timeout_seconds;
        if (countdown.seconds <= 0) isExpired = true;
      }
    } catch (err) {
      isExpired = true;
    }
  }

  async function handleAccept() {
    if (!secretId) {
      isExpired = true;
      return;
    }
    if (requiresKey && !hasValidDecryptionKey(secretKey)) {
      errorMessage = 'Decryption key is missing or incomplete in the URL. Please open the full secret link.';
      return;
    }
    isDecrypting = true;
    errorMessage = '';
    try {
      const raw = await acceptSecret(secretId);
      const plaintext = await decryptSecretClient(raw.text, secretKey);
      decryptedData = { ...raw, text: plaintext };
      if (window.location.hash) {
        window.history.replaceState(null, '', window.location.pathname + window.location.search);
      }
    } catch (err) {
      if (err?.status === 404) {
        isExpired = true;
        return;
      }
      console.error(err);
      errorMessage = err?.message || 'Failed to reveal secret. Please try again.';
    } finally {
      isDecrypting = false;
    }
  }
</script>

{#if isExpired}
  <LinkNotFound />
{:else}
  <div class="page accept-page">
    <LeftPanel {...ACCEPT_PANEL} />

    <div class="right-panel">
      <div class="accept-container">
        {#if isAccepted}
          <DecryptedSecret text={decryptedData.text} />
        {:else}
          <RevealPrompt
            remainingSeconds={countdown.seconds}
            {isDecrypting}
            {errorMessage}
            onreveal={handleAccept}
          />
        {/if}
      </div>
    </div>
  </div>
{/if}
