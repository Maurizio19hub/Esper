<script lang="ts">
  import type { Doc } from '../lib/types';
  import { KIND_LABEL, formatRelative, formatSize } from '../lib/format';
  import { app } from '../lib/store.svelte';
  import StatusBadge from './StatusBadge.svelte';
  import Thumb from './Thumb.svelte';

  let { doc, view }: { doc: Doc; view: 'grid' | 'list' } = $props();
  const shownTags = $derived(doc.tags.slice(0, 3));
  const extra = $derived(doc.tags.length - shownTags.length);
</script>

{#if view === 'grid'}
  <button class="card" onclick={() => app.openDoc(doc.id)} title={doc.name}>
    <Thumb {doc} />
    {#if doc.status !== 'indexed'}
      <span class="status"><StatusBadge {doc} /></span>
    {/if}
    {#if doc.status === 'processing'}
      <span class="bar"><span style:width="{Math.round(doc.progress * 100)}%"></span></span>
    {/if}
    <span class="body">
      <span class="name">{doc.name}</span>
      <span class="meta">{KIND_LABEL[doc.kind]} · {formatSize(doc.size)} · {formatRelative(doc.createdAt)}</span>
      <span class="tags">
        {#each shownTags as t}<span class="chip">{t}</span>{/each}
        {#if extra > 0}<span class="chip">+{extra}</span>{/if}
      </span>
    </span>
  </button>
{:else}
  <button class="row" onclick={() => app.openDoc(doc.id)} title={doc.name}>
    <Thumb {doc} compact />
    <span class="info">
      <span class="name">{doc.name}</span>
      <span class="tags">
        {#each shownTags as t}<span class="chip">{t}</span>{/each}
        {#if extra > 0}<span class="chip">+{extra}</span>{/if}
      </span>
    </span>
    <span class="cell hide-sm">{KIND_LABEL[doc.kind]}</span>
    <span class="cell hide-sm">{formatSize(doc.size)}</span>
    <span class="cell hide-sm">{formatRelative(doc.createdAt)}</span>
    <span class="cell"><StatusBadge {doc} /></span>
  </button>
{/if}

<style>
  button {
    text-align: left;
    background: var(--bg-elev);
    border: 1px solid var(--border);
    animation: rise 0.28s ease both;
    transition: border-color 0.15s, transform 0.15s, background 0.15s;
  }
  button:hover {
    border-color: var(--border-strong);
  }
  .card {
    position: relative;
    display: block;
    padding: 0;
    overflow: hidden;
    border-radius: var(--radius);
  }
  .card:hover {
    transform: translateY(-2px);
    border-color: var(--accent);
  }
  .status {
    position: absolute;
    top: 8px;
    left: 8px;
  }
  .bar {
    position: absolute;
    left: 0;
    right: 0;
    bottom: 0;
    height: 3px;
    background: var(--border);
  }
  .bar > span {
    display: block;
    height: 100%;
    background: var(--cyan);
    transition: width 0.4s ease;
  }
  .body {
    display: flex;
    flex-direction: column;
    gap: 4px;
    padding: 12px 14px 14px;
  }
  .name {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
    font-weight: 600;
    line-height: 1.35;
    word-break: break-word;
  }
  .meta {
    color: var(--text-faint);
    font-size: 12px;
  }
  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 4px;
    min-height: 22px;
  }
  .row {
    display: grid;
    grid-template-columns: auto minmax(0, 1fr) 90px 80px 130px 130px;
    align-items: center;
    gap: 14px;
    width: 100%;
    padding: 8px 14px 8px 10px;
    border-radius: 10px;
  }
  .row:hover {
    background: var(--bg-hover);
  }
  .info {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
  }
  .row .name {
    -webkit-line-clamp: 1;
    line-clamp: 1;
  }
  .cell {
    color: var(--text-dim);
    font-size: 13px;
  }
  @media (max-width: 760px) {
    .row {
      grid-template-columns: auto minmax(0, 1fr) auto;
    }
    .hide-sm {
      display: none;
    }
  }
</style>
