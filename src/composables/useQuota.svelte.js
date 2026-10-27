import { fetchDailyQuota, getDefaultQuota } from "../lib/api.js";

const POLL_INTERVAL_MS = 15000;

export function useQuota() {
  let quota = $state(getDefaultQuota());

  async function refresh() {
    quota = await fetchDailyQuota();
    return quota;
  }

  $effect(() => {
    refresh();
    const interval = setInterval(refresh, POLL_INTERVAL_MS);
    return () => clearInterval(interval);
  });

  return {
    get value() {
      return quota;
    },
    set(next) {
      quota = next;
    },
    refresh,
    /** Mark the quota as exhausted, preferring the server's numbers when provided. */
    exhaust(serverQuota) {
      quota = serverQuota || {
        ...quota,
        used: quota.limit,
        remaining: 0,
        reset_in_seconds: 60,
      };
    },
  };
}
