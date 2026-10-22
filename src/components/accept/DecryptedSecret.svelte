<script>
  import { useClipboard } from '../../composables/useClipboard.svelte.js';
  import CopyButton from '../CopyButton.svelte';
  import SecretField from './SecretField.svelte';
  import AlertTriangle from '@lucide/svelte/icons/alert-triangle';

  let { text } = $props();

  const clipboard = useClipboard();
</script>

<div class="accept-state decrypted-state">
  <div class="card-heading">
    <h2 class="accept-title">Your <span class="accent">secret</span></h2>
    <div class="shown-once-warning" role="alert">
      <AlertTriangle size={15} strokeWidth={2.2} class="warning-icon" />
      <span class="warning-text">
        <strong class="warning-strong">Shown once.</strong> Copy it before you leave this page.
      </span>
    </div>
  </div>

  {#if text}
    <SecretField {text} />
  {/if}

  <CopyButton label="Copy secret" copied={clipboard.copied} onclick={() => text && clipboard.copy(text)} />
</div>
