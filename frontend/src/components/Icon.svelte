<script lang="ts">
  import { ICONS, type IconName } from '../lib/icons';

  let { name, size = 18, stroke = 1.75, spin = false }: { name: IconName; size?: number; stroke?: number; spin?: boolean } = $props();
</script>

<svg
  class:spin
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width={stroke}
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true"
>
  {#each ICONS[name] as d}
    <path {d} />
  {/each}
</svg>
