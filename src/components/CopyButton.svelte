<script>
  import Copy from '@lucide/svelte/icons/copy';
  import Check from '@lucide/svelte/icons/check';

  let { label, copied = false, onclick, ariaLabel = label } = $props();
</script>

<button
  type="button"
  class="btn-copy {copied ? 'is-copied' : ''}"
  {onclick}
  aria-label={copied ? 'Copied to clipboard' : ariaLabel}
>
  <span class="btn-state state-default" aria-hidden={copied}>
    <Copy size={16} strokeWidth={2} class="btn-icon" />
    <span>{label}</span>
  </span>
  <span class="btn-state state-copied" aria-hidden={!copied}>
    <Check size={16} strokeWidth={2.5} class="btn-icon" />
    <span>Copied to clipboard!</span>
  </span>
</button>
