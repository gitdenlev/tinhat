<script>
  const MIN_HEIGHT = 120;
  const MAX_HEIGHT = 380;
  const MAX_LENGTH = 10000;

  let { value = $bindable(''), shake = false } = $props();

  let textareaEl = $state(null);
  let isResizing = $state(false);
  let resizeStartY = 0;
  let resizeStartHeight = 0;

  function clampHeight(height) {
    return Math.min(Math.max(height, MIN_HEIGHT), MAX_HEIGHT);
  }

  function autoResize() {
    if (!textareaEl) return;
    textareaEl.style.height = 'auto';
    textareaEl.style.height = `${clampHeight(textareaEl.scrollHeight)}px`;
  }

  // Grow/shrink with the content (also runs once the element is mounted)
  $effect(() => {
    value;
    autoResize();
  });

  // Custom resize handle (replaces the native textarea resizer)
  function startResize(e) {
    if (!textareaEl) return;
    e.preventDefault();
    isResizing = true;
    resizeStartY = e.clientY;
    resizeStartHeight = textareaEl.offsetHeight;
    e.currentTarget.setPointerCapture(e.pointerId);
  }

  function moveResize(e) {
    if (!isResizing || !textareaEl) return;
    const next = resizeStartHeight + (e.clientY - resizeStartY);
    textareaEl.style.height = `${clampHeight(next)}px`;
  }

  function endResize(e) {
    if (!isResizing) return;
    isResizing = false;
    e.currentTarget.releasePointerCapture?.(e.pointerId);
  }
</script>

<div class="tab-panel">
  <div class="text-field {shake ? 'shake' : ''}">
    <textarea
      bind:this={textareaEl}
      class="text-input"
      placeholder="Type your secret message here…"
      rows="5"
      maxlength={MAX_LENGTH}
      bind:value
    ></textarea>
    <span class="char-count">{value.length} / {MAX_LENGTH}</span>
    <div
      class="resize-handle {isResizing ? 'dragging' : ''}"
      role="separator"
      aria-orientation="horizontal"
      aria-label="Resize text field"
      onpointerdown={startResize}
      onpointermove={moveResize}
      onpointerup={endResize}
      onpointercancel={endResize}
    >
      <svg viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
        <path d="M8 2L2 8M8 6L6 8" />
      </svg>
    </div>
  </div>
</div>
