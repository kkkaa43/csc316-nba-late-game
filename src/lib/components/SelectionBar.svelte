<script>
  // Sticky summary of the game state selected in any chart (the hub of the linked views).
  import { selection, clearSelection, isSelected, pct, num2 } from '$lib/state.svelte.js';

  let { states = [], accuracy = [] } = $props();
  const s = $derived(states.find((d) => isSelected(d)));
  const a = $derived(accuracy.find((d) => isSelected(d)));
</script>

{#if s}
  <div class="selection-bar" role="region" aria-label="Selected game state">
    <div class="sel-inner">
      <span class="sel-title"><span class="sel-dot"></span>Down {s.deficit} pts · {s.time} min left</span>
      <span class="sel-metric"><b>{pct(s.comeback_rate)}</b> came back</span>
      <span class="sel-metric"><b>{pct(s.three_share)}</b> threes</span>
      <span class="sel-metric"><b>{num2(s.shots_per_min)}</b> FGA/min</span>
      {#if a}<span class="sel-metric"><b>{pct(a.fg_pct)}</b> FG</span>{/if}
      <span class="sel-hint">highlighted in every chart</span>
      <button class="sel-clear" onclick={clearSelection} aria-label="Clear the selected game state">Clear ✕</button>
    </div>
  </div>
{/if}

<style>
  .selection-bar { position: fixed; left: 50%; bottom: 16px; transform: translateX(-50%); z-index: 30; width: min(1040px, calc(100% - 24px));
    background: #102438; color: #e9f1f7; border-radius: 12px; box-shadow: 0 12px 34px #0c192955; padding: 11px 16px; }
  .sel-inner { display: flex; flex-wrap: wrap; gap: 6px 18px; align-items: center; font-size: 12.5px; }
  .sel-title { font-weight: 800; display: inline-flex; align-items: center; gap: 8px; font-family: 'Space Grotesk', sans-serif; font-size: 14px; }
  .sel-dot { width: 9px; height: 9px; border-radius: 50%; background: #f08a62; }
  .sel-metric b { color: #ffb08c; font-variant-numeric: tabular-nums; }
  .sel-hint { color: #9fb4c6; font-size: 11px; }
  .sel-clear { margin-left: auto; background: #ffffff1a; color: #fff; border: 1px solid #ffffff33; border-radius: 6px; padding: 6px 11px; font-size: 12px; font-weight: 700; cursor: pointer; }
  .sel-clear:hover, .sel-clear:focus-visible { background: #ffffff33; }
  @media (max-width: 560px) { .sel-hint { display: none; } .selection-bar { bottom: 8px; padding: 9px 12px; } }
</style>
