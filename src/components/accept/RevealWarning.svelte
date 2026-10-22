<script>
  import { formatTimeRemaining } from '../../lib/format.js';
  import AlertTriangle from '@lucide/svelte/icons/alert-triangle';
  import Clock from '@lucide/svelte/icons/clock';

  let { remainingSeconds = null } = $props();

  let timeLeft = $derived(formatTimeRemaining(remainingSeconds));
</script>

<div class="reveal-warning-box">
  <div class="warning-icon" aria-hidden="true">
    <AlertTriangle size={22} strokeWidth={2} color="#f5c842" />
  </div>
  <div class="warning-text">
    <div class="warning-header-row">
      <strong class="warning-title">Burns on first view</strong>
      {#if remainingSeconds !== null}
        <div
          class="timer-pill"
          role="status"
          aria-label="Time remaining to open secret: {timeLeft}"
          title="Time left to open this link: {timeLeft}"
        >
          <Clock size={13} strokeWidth={2.2} class="pill-clock-icon" aria-hidden="true" />
          <span class="timer-pill-text">{timeLeft} left</span>
        </div>
      {/if}
    </div>
    <span>The message will be permanently deleted from the server immediately after opening. Protects against preview bots and accidental clicks.</span>
  </div>
</div>
