<script>
  import { useNavigation } from '../composables/useNavigation.js';

  const { goTo, goHome } = useNavigation();
</script>

<header class="app-navbar">
  <a href="/" class="brand" onclick={goHome} aria-label="Tinhat home">
    <img class="brand-logo" src="/tinhat.svg" alt="Tinhat logo" width="28" height="28" />
    <span class="brand-text">Tinhat</span>
  </a>

  <nav class="nav-links">
    <a href="/privacy" class="nav-link" onclick={(e) => goTo(e, '/privacy')}>Privacy</a>
    <a href="/terms" class="nav-link" onclick={(e) => goTo(e, '/terms')}>Terms</a>
    <a
      href="https://github.com"
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
</header>

<style>
  .app-navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 48px;
    border-bottom: 1px solid #1f2438;
    background: rgba(13, 15, 26, 0.85);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    position: sticky;
    top: 0;
    z-index: 50;
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

  .nav-link:hover {
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

  @media (max-width: 600px) {
    .app-navbar {
      padding: 16px 20px;
    }

    .nav-links {
      gap: 14px;
    }
  }
</style>

