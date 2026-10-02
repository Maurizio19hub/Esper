<script lang="ts">
  import { app } from '../lib/store.svelte';
  import Icon from './Icon.svelte';
</script>

<div class="search" class:busy={app.searching}>
  <span class="lead">
    {#if app.searching}<Icon name="loader" spin />{:else}<Icon name="sparkle" />{/if}
  </span>
  <input
    id="search"
    type="search"
    autocomplete="off"
    spellcheck="false"
    placeholder="Descrivi ciò che cerchi, es. «il contratto della casa in affitto»"
    aria-label="Cerca nei documenti"
    value={app.query}
    oninput={(e) => app.setQuery(e.currentTarget.value)}
    onkeydown={(e) => {
      if (e.key === 'Escape') {
        app.setQuery('');
        e.currentTarget.blur();
      } else if (e.key === 'Enter') void app.runSearch();
    }}
  />
  {#if app.query}
    <button class="icon-btn" aria-label="Cancella ricerca" onclick={() => app.setQuery('')}><Icon name="x" /></button>
  {:else}
    <span class="kbd">/</span>
  {/if}
</div>

<style>
  .search {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
    max-width: 720px;
    height: 44px;
    padding: 0 10px 0 14px;
    background: var(--bg-elev);
    border: 1px solid var(--border-strong);
    border-radius: 999px;
    transition: border-color 0.15s, box-shadow 0.15s;
  }
  .search:focus-within {
    border-color: var(--accent);
    box-shadow: 0 0 0 4px var(--accent-soft);
  }
  .lead {
    display: grid;
    color: var(--accent);
  }
  input {
    flex: 1;
    min-width: 0;
    height: 100%;
    border: none;
    outline: none;
    background: transparent;
    font-size: 15px;
  }
  input::placeholder {
    color: var(--text-faint);
  }
  input::-webkit-search-cancel-button {
    display: none;
  }
</style>
