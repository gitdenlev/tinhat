<script>
  const SKELETON_WIDTHS = [68, 94, 82, 58, 88, 72, 44];

  let { text } = $props();

  let isMasked = $state(true);

  function toggleMask() {
    isMasked = !isMasked;
  }

  function handleClick() {
    const selection = window.getSelection();
    if (selection && selection.toString().trim().length > 0) return;
    toggleMask();
  }

  function handleKeydown(e) {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      toggleMask();
    }
  }
</script>

<div
  class="secret-field {isMasked ? 'is-masked' : 'is-revealed'}"
  onclick={handleClick}
  onkeydown={handleKeydown}
  role="button"
  tabindex="0"
  aria-label={isMasked ? 'Reveal secret' : 'Hide secret'}
>
  {#if isMasked}
    <div class="skeleton-view">
      <div class="skeleton-code-lines" aria-hidden="true">
        {#each SKELETON_WIDTHS as width}
          <div class="skeleton-line" style="width: {width}%;"></div>
        {/each}
      </div>
    </div>
  {:else}
    <div class="revealed-view">
      <div class="secret-text-content">
        {text}
      </div>
    </div>
  {/if}
</div>
