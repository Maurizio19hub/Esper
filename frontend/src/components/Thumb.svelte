<script lang="ts">
  import type { Doc } from '../lib/types';
  import { KIND_SHORT } from '../lib/format';
  import Icon from './Icon.svelte';

  let { doc, compact = false }: { doc: Doc; compact?: boolean } = $props();
</script>

<span class="thumb" class:compact class:image={doc.kind === 'image'}>
  {#if doc.kind === 'image' && doc.thumbnailUrl}
    <img src={doc.thumbnailUrl} alt="" loading="lazy" />
  {:else if compact}
    <Icon name="file-text" size={20} />
  {:else}
    <span class="paper">
      <span class="lines">{doc.excerpt || '…'}</span>
    </span>
  {/if}
  {#if !compact}<span class="kind">{KIND_SHORT[doc.kind]}</span>{/if}
</span>

<style>
  .thumb {
    position: relative;
    display: block;
    aspect-ratio: 4 / 3;
    overflow: hidden;
    background: var(--bg-elev-2);
    border-bottom: 1px solid var(--border);
  }
  .thumb.compact {
    display: grid;
    place-items: center;
    width: 44px;
    height: 44px;
    aspect-ratio: auto;
    border: 1px solid var(--border);
    border-radius: 10px;
    color: var(--text-dim);
    flex: none;
  }
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
  .compact img {
    border-radius: 9px;
  }
  .paper {
    position: absolute;
    inset: 14px 22px 0;
    padding: 12px 12px 0;
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-bottom: none;
    border-radius: 6px 6px 0 0;
    overflow: hidden;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.12);
  }
  .lines {
    display: block;
    font: 9.5px/1.45 var(--mono);
    color: var(--text-faint);
    word-break: break-word;
    -webkit-mask-image: linear-gradient(#000 55%, transparent);
    mask-image: linear-gradient(#000 55%, transparent);
  }
  .kind {
    position: absolute;
    top: 8px;
    right: 8px;
    padding: 1px 7px;
    border-radius: 6px;
    background: var(--bg);
    border: 1px solid var(--border-strong);
    color: var(--text-dim);
    font: 600 10px/16px var(--mono);
    letter-spacing: 0.04em;
  }
</style>
