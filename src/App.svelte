<script>
  import './styles/global.scss';
  import { router } from './lib/router.svelte.js';
  import Compose from './routes/Compose.svelte';
  import Accept from './routes/Accept.svelte';
  import Privacy from './routes/Privacy.svelte';
  import Terms from './routes/Terms.svelte';
  import NotFound from './routes/NotFound.svelte';
  import LinkNotFound from './routes/LinkNotFound.svelte';
  import Header from './components/Header.svelte';

  import { applySeo } from './lib/seo.js';

  // Determine current route
  let path = $derived(router.currentPath);

  // Keep title, description, canonical, robots and social tags in sync with the route
  $effect(() => {
    applySeo(path);
  });
</script>

<Header />

<main class="app-container">
  {#if path === '/' || path === '' || path === '/compose'}
    <Compose />
  {:else if path === '/accept'}
    <Accept />
  {:else if path === '/link-not-found' || path === '/expired'}
    <LinkNotFound />
  {:else if path === '/privacy'}
    <Privacy />
  {:else if path === '/terms'}
    <Terms />
  {:else}
    <NotFound />
  {/if}
</main>

<style>
  .app-container {
    width: 100%;
    min-height: calc(100vh - 73px);
    display: flex;
    flex-direction: column;
    flex: 1;
  }
</style>
