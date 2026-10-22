import { router } from '../lib/router.svelte.js';

export function useNavigation() {
  function goTo(e, path) {
    e?.preventDefault?.();
    router.navigate(path);
  }

  function goHome(e) {
    goTo(e, '/');
  }

  return { goTo, goHome };
}
