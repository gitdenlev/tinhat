/**
 * Ticking countdown. Set `seconds` once the duration is known; while `active()`
 * is true it decrements every second and calls `onExpire` when it hits zero.
 * Must be called during component initialisation (it registers an $effect).
 */
export function useCountdown({ active, onExpire }) {
  let seconds = $state(null);

  $effect(() => {
    if (seconds === null || !active()) return;

    const interval = setInterval(() => {
      if (seconds > 0) {
        seconds -= 1;
        if (seconds === 0) onExpire();
      }
    }, 1000);

    return () => clearInterval(interval);
  });

  return {
    get seconds() {
      return seconds;
    },
    set seconds(value) {
      seconds = value;
    }
  };
}
