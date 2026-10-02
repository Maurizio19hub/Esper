<script lang="ts">
  import { app } from '../lib/store.svelte';
  import { queryTerms } from '../lib/text';
  import type { MatchVia } from '../lib/types';
  import Highlight from './Highlight.svelte';
  import Icon from './Icon.svelte';
  import Thumb from './Thumb.svelte';

  const terms = $derived(queryTerms(app.query));
  const VIA: Record<MatchVia, string> = { semantic: 'semantica', keyword: 'parole chiave', both: 'ibrida' };
</script>

<div class="head">
  <h1>
    {#if app.searching && app.hits.length === 0}Ricerca in corso…{:else}{app.hits.length} {app.hits.length === 1 ? 'risultato' : 'risultati'}{/if}
  </h1>
  <p>per «{app.query.trim()}»{app.activeTags.length ? ` · etichette: ${app.activeTags.join(', ')}` : ''}</p>
</div>

{#if app.searchError}
  <div class="state"><Icon name="alert" size={26} /><p>{app.searchError}</p></div>
{:else if !app.searching && app.hits.length === 0}
  <div class="state">
    <Icon name="search" size={28} />
    <h2>Nessun documento pertinente</h2>
    <p>Prova a descrivere l’argomento con altre parole: la ricerca capisce il significato, non solo le parole esatte.</p>
  </div>
{:else}
  <ul class:stale={app.searching}>
    {#each app.hits as hit (hit.doc.id)}
      <li>
        <button onclick={() => app.openDoc(hit.doc.id)}>
          <Thumb doc={hit.doc} compact />
          <span class="main">
            <span class="top">
              <span class="name"><Highlight text={hit.doc.name} {terms} /></span>
              <span class="score" title="Pertinenza stimata">
                <span class="meter"><span style:width="{Math.round(hit.score * 100)}%"></span></span>
                {Math.round(hit.score * 100)}%
              </span>
            </span>
            {#each hit.matches.slice(0, 2) as m (m.chunkId)}
              <span class="snippet">
                <span class="via {m.via}">{VIA[m.via]}</span>
                {#if m.page}<span class="page">p. {m.page}</span>{/if}
                <span class="text"><Highlight text={m.text} {terms} /></span>
              </span>
            {:else}
              <span class="snippet"><span class="text">{hit.doc.excerpt}</span></span>
            {/each}
            {#if hit.doc.tags.length}
              <span class="tags">{#each hit.doc.tags as t}<span class="chip">{t}</span>{/each}</span>
            {/if}
          </span>
        </button>
      </li>
    {/each}
  </ul>
{/if}

<style>
  .head {
    margin-bottom: 16px;
  }
  h1 {
    font-size: 22px;
  }
  .head p {
    color: var(--text-dim);
  }
  ul {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
    transition: opacity 0.2s;
  }
  ul.stale {
    opacity: 0.5;
  }
  li button {
    display: flex;
    gap: 14px;
    width: 100%;
    padding: 14px;
    text-align: left;
    background: var(--bg-elev);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    animation: rise 0.25s ease both;
    transition: border-color 0.15s;
  }
  li button:hover {
    border-color: var(--accent);
  }
  .main {
    display: flex;
    flex-direction: column;
    gap: 8px;
    min-width: 0;
    flex: 1;
  }
  .top {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
  }
  .name {
    font-weight: 600;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .score {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font: 12px var(--mono);
    color: var(--text-dim);
    flex: none;
  }
  .meter {
    width: 64px;
    height: 4px;
    border-radius: 2px;
    background: var(--border-strong);
    overflow: hidden;
  }
  .meter > span {
    display: block;
    height: 100%;
    background: linear-gradient(90deg, var(--cyan), var(--accent));
  }
  .snippet {
    display: flex;
    gap: 8px;
    align-items: baseline;
    color: var(--text-dim);
    font-size: 13px;
  }
  .text {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
  .via,
  .page {
    flex: none;
    font: 600 10.5px var(--mono);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 1px 6px;
    border-radius: 5px;
  }
  .via.semantic {
    background: var(--cyan-soft);
    color: var(--cyan);
  }
  .via.keyword {
    background: var(--bg-hover);
    color: var(--text-dim);
  }
  .via.both {
    background: var(--accent-soft);
    color: var(--accent);
  }
  .page {
    color: var(--text-faint);
  }
  .tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }
  .state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    margin: 8vh auto 0;
    max-width: 420px;
    text-align: center;
    color: var(--text-dim);
  }
  .state h2 {
    color: var(--text);
    font-size: 19px;
  }
</style>
