export function useClipboard(duration = 2000) {
  let copied = $state(false);
  let timer = null;

  function copy(text) {
    if (!text) return false;

    const fallbackCopy = (t) => {
      const ta = document.createElement('textarea');
      ta.value = t;
      ta.style.position = 'fixed';
      ta.style.opacity = '0';
      document.body.appendChild(ta);
      ta.focus();
      ta.select();
      try {
        document.execCommand('copy');
      } catch (_) {}
      document.body.removeChild(ta);
    };

    if (typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
      navigator.clipboard.writeText(text).catch(() => fallbackCopy(text));
    } else {
      fallbackCopy(text);
    }

    copied = true;
    if (timer) clearTimeout(timer);
    timer = setTimeout(() => {
      copied = false;
    }, duration);

    return true;
  }

  return {
    get copied() {
      return copied;
    },
    copy,
  };
}