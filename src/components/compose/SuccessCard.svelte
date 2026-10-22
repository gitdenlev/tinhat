<script>
  import { useClipboard } from '../../composables/useClipboard.svelte.js';
  import { generateQrSvg } from '../../lib/qr.js';
  import CopyButton from '../CopyButton.svelte';
  import Link from '@lucide/svelte/icons/link';
  import QrCode from '@lucide/svelte/icons/qr-code';

  let { url } = $props();

  const clipboard = useClipboard();

  let showQr = $state(false);
  let qrSvg = $state('');

  $effect(() => {
    generateQrSvg(url).then((svg) => { qrSvg = svg; });
  });

  function selectOnClick(e) {
    e.currentTarget.select();
  }
</script>

<div class="success-card" role="region" aria-label="Generated secret link">
  <div class="success-card-header">
    <div class="success-header-text">
      <h3 class="success-card-title">{showQr ? 'Secret QR code' : 'Secret link ready'}</h3>
      <p class="success-card-sub">
        {showQr ? 'Scan with your mobile camera to open secret.' : 'Shown once. Copy it now.'}
      </p>
    </div>

    <button
      type="button"
      class="btn-qr-toggle"
      onclick={() => { showQr = !showQr; }}
      title={showQr ? 'Show secret link' : 'Show QR code'}
      aria-label={showQr ? 'Show secret link' : 'Show QR code'}
    >
      {#if showQr}
        <Link size={17} strokeWidth={2.2} class="toggle-icon" aria-hidden="true" />
      {:else}
        <QrCode size={17} strokeWidth={2.2} class="toggle-icon" aria-hidden="true" />
      {/if}
    </button>
  </div>

  {#if !showQr}
    <div class="link-field-box view-swap">
      <input
        type="text"
        class="link-url-text"
        readonly
        value={url}
        onclick={selectOnClick}
        aria-label="Secret link URL"
      />
    </div>
  {:else}
    <div class="qr-field-box view-swap">
      <div class="qr-code-frame">
        {#if qrSvg}
          {@html qrSvg}
        {/if}
      </div>
    </div>
  {/if}

  <CopyButton label="Copy link" ariaLabel="Copy secret link" copied={clipboard.copied} onclick={() => clipboard.copy(url)} />
</div>
