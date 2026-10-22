export function formatWaitTime(seconds) {
  if (!seconds || seconds <= 0) return 'a moment';
  if (seconds < 60) {
    const secs = Math.max(1, Math.ceil(seconds));
    return secs === 1 ? '1 second' : `${secs} seconds`;
  }
  const hrs = Math.floor(seconds / 3600);
  const mins = Math.ceil((seconds % 3600) / 60);
  if (hrs > 0 && mins > 0 && mins < 60) return `${hrs}h ${mins}m`;
  if (hrs > 0) return hrs === 1 ? '1 hour' : `${hrs} hours`;
  const safeMins = Math.max(1, mins);
  return safeMins === 1 ? '1 minute' : `${safeMins} minutes`;
}

/** Countdown label, e.g. "1d 02h 05m 09s". */
export function formatTimeRemaining(totalSec) {
  if (totalSec == null) return '';
  if (totalSec <= 0) return '00:00';
  const d = Math.floor(totalSec / 86400);
  const h = Math.floor((totalSec % 86400) / 3600);
  const m = Math.floor((totalSec % 3600) / 60);
  const s = totalSec % 60;

  const pad = (n) => String(n).padStart(2, '0');

  if (d > 0) return `${d}d ${pad(h)}h ${pad(m)}m ${pad(s)}s`;
  if (h > 0) return `${pad(h)}h ${pad(m)}m ${pad(s)}s`;
  return `${pad(m)}m ${pad(s)}s`;
}
