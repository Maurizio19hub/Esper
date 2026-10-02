<script lang="ts">
  import { highlight } from '../lib/text';

  let { text, terms }: { text: string; terms: string[] } = $props();
  const segments = $derived(highlight(text, terms));
</script>

{#each segments as s}{#if s.hit}<mark>{s.text}</mark>{:else}{s.text}{/if}{/each}
