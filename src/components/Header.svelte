<script>
  import { useNavigation } from '../composables/useNavigation.js';
  import { router } from '../lib/router.svelte.js';
  import Shield from '@lucide/svelte/icons/shield';
  import FileText from '@lucide/svelte/icons/file-text';
  import ArrowUpRight from '@lucide/svelte/icons/arrow-up-right';

  const { goTo, goHome } = useNavigation();

  let menuOpen = $state(false);
  let currentPath = $derived(router.currentPath);

  $effect(() => {
    currentPath;
    menuOpen = false;
  });

  function toggleMenu() {
    menuOpen = !menuOpen;
  }

  function closeMenu() {
    menuOpen = false;
  }

  function handleNav(e, path) {
    menuOpen = false;
    goTo(e, path);
  }

  function handleHome(e) {
    menuOpen = false;
    goHome(e);
  }

  function handleKeydown(e) {
    if (e.key === 'Escape' && menuOpen) {
      menuOpen = false;
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if menuOpen}
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="mobile-menu-backdrop" onclick={closeMenu}></div>
{/if}

<header class="app-navbar">
  <a href="/" class="brand" onclick={handleHome} aria-label="Tinhat home">
    <img class="brand-logo" src="/tinhat.svg" alt="Tinhat logo" width="28" height="28" />
    <span class="brand-text">Tinhat</span>
  </a>

  <nav class="nav-links" aria-label="Primary navigation">
    <a
      href="/privacy"
      class="nav-link"
      class:active={currentPath === '/privacy'}
      onclick={(e) => handleNav(e, '/privacy')}
    >
      Privacy
    </a>
    <a
      href="/terms"
      class="nav-link"
      class:active={currentPath === '/terms'}
      onclick={(e) => handleNav(e, '/terms')}
    >
      Terms
    </a>
    <a
      href="https://github.com/gitdenlev/tinhat"
      target="_blank"
      rel="noopener noreferrer"
      class="nav-link github-link"
      aria-label="GitHub repository"
    >
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
      </svg>
      <span>GitHub</span>
    </a>
  </nav>

  <button
    type="button"
    class="burger-btn"
    class:is-open={menuOpen}
    onclick={toggleMenu}
    aria-label={menuOpen ? 'Close navigation menu' : 'Open navigation menu'}
    aria-expanded={menuOpen}
    aria-controls="mobile-nav-menu"
  >
    <span class="burger-box" aria-hidden="true">
      <span class="burger-line line-1"></span>
      <span class="burger-line line-2"></span>
      <span class="burger-line line-3"></span>
    </span>
  </button>

  {#if menuOpen}
    <nav id="mobile-nav-menu" class="mobile-menu" aria-label="Mobile navigation">
      <a
        href="/privacy"
        class="mobile-nav-item"
        class:active={currentPath === '/privacy'}
        onclick={(e) => handleNav(e, '/privacy')}
      >
        <span class="mobile-nav-item-left">
          <Shield size={16} strokeWidth={2} class="mobile-nav-icon" />
          <span>Privacy Policy</span>
        </span>
      </a>

      <a
        href="/terms"
        class="mobile-nav-item"
        class:active={currentPath === '/terms'}
        onclick={(e) => handleNav(e, '/terms')}
      >
        <span class="mobile-nav-item-left">
          <FileText size={16} strokeWidth={2} class="mobile-nav-icon" />
          <span>Terms of Service</span>
        </span>
      </a>

      <div class="mobile-menu-divider" role="separator"></div>

      <a
        href="https://github.com/gitdenlev/tinhat"
        target="_blank"
        rel="noopener noreferrer"
        class="mobile-nav-item github-mobile-item"
        onclick={closeMenu}
      >
        <span class="mobile-nav-item-left">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="mobile-nav-icon">
            <path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"/>
          </svg>
          <span>GitHub</span>
        </span>
        <ArrowUpRight size={15} strokeWidth={2} class="external-icon" />
      </a>
    </nav>
  {/if}
</header>

<style>
  .app-navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 48px;
    border-bottom: 1px solid #1f2438;
    background: rgba(13, 15, 26, 0.88);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 60;
    width: 100%;
    box-sizing: border-box;
  }

  .brand {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    text-decoration: none;
    color: inherit;
    transition: opacity 0.15s ease, transform 0.15s ease;
  }

  .brand:hover {
    opacity: 0.92;
    transform: translateY(-0.5px);
  }

  .brand-logo {
    width: 28px;
    height: 28px;
    display: block;
    object-fit: contain;
    flex-shrink: 0;
    filter: drop-shadow(0 2px 8px rgba(245, 196, 67, 0.28));
  }

  .brand-text {
    font-size: 23px;
    line-height: 1;
    letter-spacing: -0.5px;
    font-weight: 800;
    color: #ffffff;
    display: inline-flex;
    align-items: center;
  }

  .nav-links {
    display: flex;
    align-items: center;
    gap: 22px;
  }

  .nav-link {
    color: #8b92ad;
    text-decoration: none;
    font-size: 13.5px;
    font-weight: 600;
    transition: color 0.15s ease;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }

  .nav-link:hover,
  .nav-link.active {
    color: #f5c842;
  }

  .github-link {
    padding: 6px 12px;
    border-radius: 8px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .github-link:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: rgba(245, 200, 66, 0.35);
  }

  /* ── Burger Button (Tablet & Mobile) ─────────────────────────────── */
  .burger-btn {
    display: none;
    align-items: center;
    justify-content: center;
    width: 38px;
    height: 38px;
    padding: 0;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #dfe4f7;
    cursor: pointer;
    transition: background 0.15s ease, border-color 0.15s ease, color 0.15s ease, box-shadow 0.15s ease;
    -webkit-tap-highlight-color: transparent;
  }

  .burger-btn:hover,
  .burger-btn.is-open {
    background: rgba(245, 200, 66, 0.1);
    border-color: rgba(245, 200, 66, 0.45);
    color: #f5c842;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.35);
  }

  .burger-btn:focus-visible {
    outline: 2px solid #f5c842;
    outline-offset: 2px;
  }

  .burger-box {
    position: relative;
    width: 18px;
    height: 14px;
    display: inline-block;
  }

  .burger-line {
    position: absolute;
    left: 0;
    width: 100%;
    height: 2px;
    border-radius: 2px;
    background: currentColor;
    transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1),
      opacity 0.18s ease,
      top 0.22s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .line-1 {
    top: 0;
  }

  .line-2 {
    top: 6px;
  }

  .line-3 {
    top: 12px;
  }

  .burger-btn.is-open .line-1 {
    top: 6px;
    transform: rotate(45deg);
  }

  .burger-btn.is-open .line-2 {
    opacity: 0;
    transform: scaleX(0.4);
  }

  .burger-btn.is-open .line-3 {
    top: 6px;
    transform: rotate(-45deg);
  }

  /* ── Mobile Menu Backdrop & Dropdown Card ────────────────────────── */
  .mobile-menu-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(5, 7, 16, 0.48);
    backdrop-filter: blur(3px);
    -webkit-backdrop-filter: blur(3px);
    z-index: 55;
    animation: backdrop-fade 0.18s ease-out;
  }

  .mobile-menu {
    position: absolute;
    top: calc(100% + 8px);
    right: 28px;
    width: min(260px, calc(100vw - 32px));
    background: #141728;
    border: 1.5px solid #2f3659;
    border-radius: 14px;
    padding: 8px;
    box-shadow: 0 18px 42px rgba(0, 0, 0, 0.65), 0 0 18px rgba(0, 0, 0, 0.35);
    display: flex;
    flex-direction: column;
    gap: 3px;
    z-index: 65;
    animation: menu-pop 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .mobile-nav-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 11px 12px;
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    color: #c9d1ec;
    text-decoration: none;
    transition: background 0.15s ease, color 0.15s ease;
  }

  .mobile-nav-item-left {
    display: inline-flex;
    align-items: center;
    gap: 10px;
  }

  .mobile-nav-item :global(.mobile-nav-icon) {
    color: #8b92ad;
    flex-shrink: 0;
    transition: color 0.15s ease;
  }

  .mobile-nav-item :global(.external-icon) {
    color: #767fa2;
    flex-shrink: 0;
    transition: color 0.15s ease, transform 0.15s ease;
  }

  .mobile-nav-item:hover,
  .mobile-nav-item:active {
    background: rgba(245, 200, 66, 0.1);
    color: #ffffff;
  }

  .mobile-nav-item:hover :global(.mobile-nav-icon),
  .mobile-nav-item:active :global(.mobile-nav-icon) {
    color: #f5c842;
  }

  .mobile-nav-item:hover :global(.external-icon) {
    color: #f5c842;
    transform: translate(1px, -1px);
  }

  .mobile-nav-item.active {
    background: rgba(245, 200, 66, 0.14);
    color: #f5c842;
  }

  .mobile-nav-item.active :global(.mobile-nav-icon) {
    color: #f5c842;
  }

  .mobile-menu-divider {
    height: 1px;
    background: rgba(255, 255, 255, 0.07);
    margin: 4px 6px;
  }

  @keyframes menu-pop {
    from {
      opacity: 0;
      transform: translateY(-6px) scale(0.97);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  @keyframes backdrop-fade {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @media (max-width: 1024px) {
    .app-navbar {
      padding: 13px 28px;
    }

    .nav-links {
      display: none;
    }

    .burger-btn {
      display: inline-flex;
    }
  }

  @media (max-width: 480px) {
    .app-navbar {
      padding: 11px 16px;
    }

    .brand {
      gap: 8px;
    }

    .brand-logo {
      width: 25px;
      height: 25px;
    }

    .brand-text {
      font-size: 20px;
    }

    .mobile-menu {
      right: 16px;
      left: 16px;
      width: auto;
    }
  }
</style>

