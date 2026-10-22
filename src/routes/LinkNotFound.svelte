<script>
  import LeftPanel from '../components/LeftPanel.svelte';
  import { LINK_NOT_FOUND_PANEL } from '../lib/content.js';
  import { useNavigation } from '../composables/useNavigation.js';
  import AlertTriangle from '@lucide/svelte/icons/alert-triangle';
  import Plus from '@lucide/svelte/icons/plus';

  const { goHome } = useNavigation();

  let {
    title = 'Failed: <span class="accent">Link does not exist</span>'
  } = $props();
</script>

<div class="page link-not-found-page">
  <LeftPanel {...LINK_NOT_FOUND_PANEL} />

  <div class="right-panel">
    <div class="lnf-container">
      <!-- Heading -->
      <div class="card-heading">
        <h2 class="lnf-title">{@html title}</h2>
      </div>

      <!-- Explanatory Notice Box -->
      <div class="lnf-notice-box">
        <div class="notice-icon" aria-hidden="true">
          <AlertTriangle size={22} strokeWidth={2} />
        </div>
        <div class="notice-text">
          <strong class="notice-title">Why can't this link be opened?</strong>
          <ul class="notice-list">
            <li><strong>Already viewed:</strong> Someone already opened this link, triggering instant self-destruction.</li>
            <li><strong>Timer expired:</strong> The link reached its lifetime limit before being opened.</li>
            <li><strong>Incorrect address:</strong> A character might be missing or cut off from the URL.</li>
          </ul>
        </div>
      </div>

      <!-- Action Button -->
      <div class="action-row">
        <a href="/" class="btn-create-new" onclick={goHome}>
          <Plus size={19} strokeWidth={2.5} class="btn-action-icon" />
          <span>Create a new secret</span>
        </a>
      </div>

      <!-- Footer Privacy Note -->
      <div class="lnf-footer">
        <p class="privacy-note">Links cannot be restored once burned. If this link was sent to you, request a new one.</p>
      </div>
    </div>
  </div>
</div>
