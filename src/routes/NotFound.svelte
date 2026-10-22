<script>
  import { useNavigation } from '../composables/useNavigation.js';
  import Plus from '@lucide/svelte/icons/plus';

  const { goHome } = useNavigation();

  let {
    code = '404',
    title = 'Page not found',
    subtitle = 'This secret has self-destructed, expired, or never existed in the first place.'
  } = $props();
</script>

<div class="nf-page">
  <div class="nf-main">
    <div class="nf-container">
      <div class="number-wrapper">
        <span class="huge-number">{code}</span>
      </div>

      <h1 class="headline">{title}</h1>
      <p class="description">{subtitle}</p>

      <div class="actions">
        <a href="/" class="btn-home" onclick={goHome}>
          <Plus size={19} strokeWidth={2.5} />
          <span>Create a new secret</span>
        </a>
      </div>
    </div>
  </div>
</div>

<style>
  .number-wrapper {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 8px;
  }

  .huge-number {
    font-size: clamp(100px, 18vw, 170px);
    font-weight: 900;
    letter-spacing: -6px;
    line-height: 0.9;
    background: linear-gradient(180deg, #ffffff 15%, rgba(255, 255, 255, 0.15) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    user-select: none;
  }

  .actions {
    margin-top: 28px;
    display: flex;
    justify-content: center;
  }

  .btn-home {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    height: 48px;
    padding: 0 24px;
    font-size: 15px;
    font-weight: 700;
    border-radius: 12px;
    background: #f5c842;
    color: #0d0f1a;
    text-decoration: none;
    transition: background 0.15s ease, transform 0.12s ease, box-shadow 0.15s ease;
  }

  .btn-home:hover {
    background: #e6b830;
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(245, 200, 66, 0.25);
  }

  .btn-home:active {
    transform: translateY(0);
  }
</style>
