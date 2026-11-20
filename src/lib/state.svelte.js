// Shared state and constants for the linked views.
//
// Every chart reads `selection` and calls `selectState(...)`. Picking a game state
// (deficit band x time window) in any chart highlights the same state in all the others,
// re-filters the team comparison (H4), and updates the sticky summary bar.
import * as d3 from 'd3';

export const DEFICITS = ['1–3', '4–6', '7–10', '11+'];
// Display order: start of the fourth quarter first, final minutes last.
export const TIMES = ['9–12', '6–9', '3–6', '0–3'];

export const selection = $state({ deficit: null, time: null });

/** Select a game state; selecting the active state again clears it. */
export function selectState(deficit, time) {
  if (selection.deficit === deficit && selection.time === time) clearSelection();
  else {
    selection.deficit = deficit;
    selection.time = time;
  }
}

export function clearSelection() {
  selection.deficit = null;
  selection.time = null;
}

export const isSelected = (d) => selection.deficit === d.deficit && selection.time === d.time;
export const hasSelection = () => selection.deficit !== null;

// Ordinal colours for time windows: cool = early in the quarter, warm = the final minutes.
export const TIME_COLORS = { '9–12': '#7f98b0', '6–9': '#3f6e96', '3–6': '#e8955a', '0–3': '#c8441d' };
// Ordinal colours for deficit bands: light teal (close game) -> dark navy (blowout).
export const DEFICIT_COLORS = { '1–3': '#5fb8b3', '4–6': '#2b8a8f', '7–10': '#22607f', '11+': '#1b3554' };
export const ACCENT = '#c8441d';
export const INK = '#17273b';
export const MUTED = '#5b6b7c';

export const pct = d3.format('.1%');
export const pct0 = d3.format('.0%');
export const num2 = (v) => (Number.isFinite(v) ? v.toFixed(2) : 'n/a');
export const timeLabel = (t) => `${t} min left`;
export const deficitLabel = (d) => `down ${d}`;
export const stateLabel = (d, t) => `Down ${d} pts · ${t} min left`;

/**
 * Make an SVG element behave like a button for mouse and keyboard users.
 * `key` lets a chart restore focus after it re-renders.
 */
export function asButton(sel, { label, key, onActivate }) {
  sel
    .attr('tabindex', 0)
    .attr('role', 'button')
    .attr('aria-label', label)
    .attr('data-key', key)
    .style('cursor', 'pointer')
    .on('click', (event, d) => onActivate(d, event))
    .on('keydown', (event, d) => {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        onActivate(d, event);
      }
    });
  return sel;
}

/** After a re-render, put keyboard focus back on the element that had it. */
export function restoreFocus(root, key) {
  if (!root || !key) return;
  const el = root.querySelector(`[data-key="${CSS.escape(key)}"]`);
  if (el) el.focus({ preventScroll: true });
}

/** Wilson 95% interval for a proportion k/n. */
export function wilson(k, n, z = 1.96) {
  if (!n) return [NaN, NaN];
  const p = k / n;
  const den = 1 + (z * z) / n;
  const centre = (p + (z * z) / (2 * n)) / den;
  const half = (z * Math.sqrt((p * (1 - p)) / n + (z * z) / (4 * n * n))) / den;
  return [Math.max(0, centre - half), Math.min(1, centre + half)];
}
