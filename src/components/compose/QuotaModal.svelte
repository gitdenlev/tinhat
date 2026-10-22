<script>
  import AlertTriangle from '@lucide/svelte/icons/alert-triangle';
  import { formatWaitTime } from '../../lib/format.js';

  let { resetInSeconds, onclose } = $props();
</script>

<!-- svelte-ignore a11y_no_static_element_interactions -->
<div
  class="modal-backdrop"
  onclick={(e) => { if (e.target === e.currentTarget) onclose(); }}
  onkeydown={(e) => { if (e.key === 'Escape') onclose(); }}
  role="dialog"
  aria-modal="true"
  aria-labelledby="quota-modal-title"
  tabindex="-1"
>
  <div class="modal-card">
    <div class="modal-header">
      <div class="modal-icon" aria-hidden="true">
        <AlertTriangle size={24} strokeWidth={2.2} />
      </div>
      <h3 id="quota-modal-title" class="modal-title">Quota limit reached</h3>
    </div>

    <p class="modal-desc">
      You've reached your quota for generating secret links right now. Please come back in <strong class="quota-wait-highlight">{formatWaitTime(resetInSeconds)}</strong> to create a new link.
    </p>

    <div class="modal-actions">
      <button type="button" class="btn-modal-primary" onclick={onclose}>
        Got it
      </button>
    </div>
  </div>
</div>
