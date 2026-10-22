<script>
  import Clock from '@lucide/svelte/icons/clock';
  import ChevronDown from '@lucide/svelte/icons/chevron-down';
  import Check from '@lucide/svelte/icons/check';

  const OPTIONS = [
    { val: 300, label: '5 min', full: '5 minutes' },
    { val: 3600, label: '1 hour', full: '1 hour' },
    { val: 21600, label: '6 hours', full: '6 hours' },
    { val: 86400, label: '24 hours', full: '24 hours' }
  ];

  let { value = $bindable(3600) } = $props();

  let isOpen = $state(false);

  let currentLabel = $derived(OPTIONS.find((o) => o.val === value)?.label || '1 hour');

  function select(val) {
    value = val;
    isOpen = false;
  }

  function handleGlobalClick(e) {
    if (!e.target.closest('.lifetime-dropdown-wrap')) isOpen = false;
  }

  // Close the menu when clicking anywhere outside of it
  $effect(() => {
    if (!isOpen) return;
    window.addEventListener('click', handleGlobalClick);
    return () => window.removeEventListener('click', handleGlobalClick);
  });
</script>

<div class="lifetime-dropdown-wrap">
  <button
    type="button"
    class="lifetime-pill-btn {isOpen ? 'is-open' : ''}"
    onclick={(e) => {
      e.stopPropagation();
      isOpen = !isOpen;
    }}
    aria-haspopup="listbox"
    aria-expanded={isOpen}
    title="Secret lifetime: {currentLabel}"
  >
    <Clock size={13} strokeWidth={2.2} class="pill-clock-icon" aria-hidden="true" />
    <span class="pill-label">{currentLabel}</span>
    <ChevronDown size={12} strokeWidth={2.3} class="pill-chevron {isOpen ? 'rotate' : ''}" aria-hidden="true" />
  </button>

  {#if isOpen}
    <div class="lifetime-menu" role="listbox" aria-label="Secret lifetime options">
      <div class="menu-header">Expires in</div>
      {#each OPTIONS as opt}
        <button
          type="button"
          role="option"
          aria-selected={value === opt.val}
          class="lifetime-menu-item {value === opt.val ? 'selected' : ''}"
          onclick={() => select(opt.val)}
        >
          <span class="item-label">{opt.full}</span>
          {#if value === opt.val}
            <Check size={14} strokeWidth={2.5} class="item-check" />
          {/if}
        </button>
      {/each}
    </div>
  {/if}
</div>
