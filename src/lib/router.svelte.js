export class Router {
  currentPath = $state(window.location.pathname || '/');
  search = $state(window.location.search || '');
  hash = $state(window.location.hash || '');
  searchParams = $derived(new URLSearchParams(this.search));

  constructor() {
    const sync = () => {
      this.currentPath = window.location.pathname;
      this.search = window.location.search;
      this.hash = window.location.hash;
    };
    window.addEventListener('popstate', sync);
    window.addEventListener('hashchange', sync);
  }

  navigate(to) {
    if (to.startsWith('/')) {
      const url = new URL(to, window.location.origin);
      window.history.pushState({}, '', to);
      this.currentPath = url.pathname;
      this.search = url.search;
      this.hash = url.hash;
      window.scrollTo(0, 0);
    } else {
      window.location.href = to;
    }
  }
}

export const router = new Router();
