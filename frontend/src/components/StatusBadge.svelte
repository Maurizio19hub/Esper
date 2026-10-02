<script lang="ts">
  import type { Doc } from '../lib/types';
  import { STATUS_LABEL } from '../lib/format';
  import Icon from './Icon.svelte';

  let { doc }: { doc: Doc } = $props();
  const pct = $derived(Math.round(doc.progress * 100));
</script>

<span class="badge {doc.status}">
  {#if doc.status === 'processing'}
    <Icon name="loader" size={12} spin />
  {:else if doc.status === 'queued'}
    <Icon name="clock" size={12} />
  {:else if doc.status === 'error'}
    <Icon name="alert" size={12} />
  {:else}
    <Icon name="check" size={12} stroke={2.2} />
  {/if}
  {STATUS_LABEL[doc.status]}{doc.status === 'processing' ? ` ${pct}%` : ''}
</span>

<style>
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    height: 22px;
    padding: 0 8px;
    border-radius: 999px;
    font-size: 11.5px;
    font-weight: 500;
    white-space: nowrap;
  }
  .indexed {
    background: var(--ok-soft);
    color: var(--ok);
  }
  .processing {
    background: var(--cyan-soft);
    color: var(--cyan);
  }
  .queued {
    background: var(--bg-hover);
    color: var(--text-dim);
  }
  .error {
    background: var(--err-soft);
    color: var(--err);
  }
</style>
