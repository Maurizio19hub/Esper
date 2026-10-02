<script lang="ts">
  let { size = 30 }: { size?: number } = $props();
</script>

<svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden="true">
  <rect width="32" height="32" rx="9" fill="var(--bg-elev-2)" stroke="var(--border-strong)" />
  <circle cx="16" cy="16" r="9.5" stroke="var(--accent)" stroke-width="1.6" />
  <circle cx="16" cy="16" r="5" stroke="var(--cyan)" stroke-width="1.2" stroke-opacity=".7" />
  <circle cx="16" cy="16" r="2.2" fill="var(--accent)" />
  <path d="M16 3.5v4M16 24.5v4M3.5 16h4M24.5 16h4" stroke="var(--accent)" stroke-width="1.4" stroke-linecap="round" />
</svg>
