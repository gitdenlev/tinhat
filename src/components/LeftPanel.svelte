<script>
  import Clock from '@lucide/svelte/icons/clock';
  import Shield from '@lucide/svelte/icons/shield';
  import Flame from '@lucide/svelte/icons/flame';
  import Ghost from '@lucide/svelte/icons/ghost';

  const ICONS = { clock: Clock, flame: Flame, ghost: Ghost, shield: Shield };

  let {
    title = 'Share secrets that<br/>delete themselves.',
    subtitle = 'Send confidential text with a link. You decide how long it<br/>lives and when it self-destructs.',
    features = [
      {
        icon: 'clock',
        title: 'Auto-delete',
        desc: 'Every secret disappears permanently after the time you choose.'
      },
      {
        icon: 'shield',
        title: 'End-to-end encrypted',
        desc: 'Encrypted in your browser. Zero server logs.'
      },
      {
        icon: 'ghost',
        title: 'Zero trace left behind',
        desc: 'No accounts, no history, no logs stored anywhere.'
      }
    ]
  } = $props();
</script>

<div class="left-panel">
  <!-- Hero -->
  <div class="hero">
    <h1 class="hero-title">{@html title}</h1>
    <p class="hero-subtitle">{@html subtitle}</p>
  </div>

  <!-- Features -->
  <ul class="features">
    {#each features as f}
      {@const Icon = ICONS[f.icon] ?? Shield}
      <li class="feature">
        <div class="feature-icon">
          <Icon size={19} strokeWidth={2} />
        </div>
        <div class="feature-text">
          <strong>{f.title}</strong>
          <span>{f.desc}</span>
        </div>
      </li>
    {/each}
  </ul>

  <!-- Decorative circle -->
  <div class="deco-circle"></div>
</div>
