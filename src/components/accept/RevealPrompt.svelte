<script>
  import RevealWarning from './RevealWarning.svelte';
  import Eye from '@lucide/svelte/icons/eye';
  import LoaderCircle from '@lucide/svelte/icons/loader-circle';

  let { remainingSeconds = null, isDecrypting = false, errorMessage = '', onreveal } = $props();
</script>

<div class="accept-state">
  <div class="card-heading">
    <h2 class="accept-title">Reveal this <span class="accent">secret?</span></h2>
    <p class="accept-sub">This secret can only be opened once. Click below to reveal and burn it.</p>
  </div>

  <RevealWarning {remainingSeconds} />

  {#if errorMessage}
    <p class="reveal-error-msg">{errorMessage}</p>
  {/if}

  <div class="action-row">
    <button
      type="button"
      class="btn-reveal"
      onclick={onreveal}
      disabled={isDecrypting}
    >
      {#if isDecrypting}
        <LoaderCircle size={16} strokeWidth={2.5} class="spin-icon" />
        <span>Decrypting…</span>
      {:else}
        <Eye size={18} strokeWidth={2.2} />
        <span>Reveal secret</span>
      {/if}
    </button>
  </div>

  <div class="accept-footer">
    <p class="privacy-note">Links cannot be revoked. Open only when you're ready to view it.</p>
  </div>
</div>
