<script lang="ts">
  import { app, apiMode } from '../lib/store.svelte';
  import Icon from './Icon.svelte';
  import Logo from './Logo.svelte';
</script>

{#if app.sidebarOpen}
  <button class="scrim" aria-label="Chiudi menu" onclick={() => (app.sidebarOpen = false)}></button>
{/if}

<aside class:open={app.sidebarOpen}>
  <div class="brand">
    <Logo />
    <div>
      <div class="title">Esper</div>
      <div class="sub">archivio semantico</div>
    </div>
  </div>

  <nav aria-label="Navigazione">
    <button class="nav" class:active={app.activeTags.length === 0} onclick={() => { app.clearFilters(); app.sidebarOpen = false; }}>
      <Icon name="library" /> Libreria
      <span class="count">{app.docs.length}</span>
    </button>
  </nav>

  <div class="section">
    <h2>Etichette</h2>
    {#if app.tagList.length === 0}
      <p class="empty">Nessuna etichetta ancora.</p>
    {/if}
    <div class="tags">
      {#each app.tagList as t (t.name)}
        <button class="tag" class:active={app.activeTags.includes(t.name)} aria-pressed={app.activeTags.includes(t.name)} onclick={() => app.toggleTag(t.name)}>
          <Icon name="tag" size={14} />
          <span class="n">{t.name}</span>
          <span class="count">{t.count}</span>
        </button>
      {/each}
    </div>
  </div>

  <div class="foot">
    {#if apiMode === 'mock'}
      <div class="demo" title="I documenti e la ricerca sono simulati: il backend non è ancora collegato.">
        <Icon name="alert" size={14} /> Modalità demo · dati simulati
      </div>
    {/if}
    <div class="stats">
      <Icon name="layers" size={14} />
      {app.docs.length} documenti · {app.totalChunks} frammenti
    </div>
    <button class="btn btn-ghost theme" onclick={() => app.toggleTheme()}>
      <Icon name={app.theme === 'dark' ? 'sun' : 'moon'} />
      Tema {app.theme === 'dark' ? 'chiaro' : 'scuro'}
    </button>
  </div>
</aside>

<style>
  aside {
    display: flex;
    flex-direction: column;
    gap: 18px;
    width: 264px;
    height: 100%;
    padding: 18px 14px;
    background: var(--bg-elev);
    border-right: 1px solid var(--border);
    overflow: hidden;
    flex: none;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 2px 6px 6px;
  }
  .title {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.04em;
  }
  .sub {
    font: 11px var(--mono);
    color: var(--text-faint);
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }
  .nav,
  .tag {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
    height: 36px;
    padding: 0 10px;
    border: 1px solid transparent;
    border-radius: var(--radius-sm);
    background: transparent;
    color: var(--text-dim);
    text-align: left;
    transition: background 0.15s, color 0.15s;
  }
  .nav:hover,
  .tag:hover {
    background: var(--bg-hover);
    color: var(--text);
  }
  .nav.active {
    background: var(--accent-soft);
    color: var(--accent);
    font-weight: 600;
  }
  .tag.active {
    background: var(--cyan-soft);
    color: var(--cyan);
    border-color: var(--cyan-soft);
    font-weight: 600;
  }
  .count {
    margin-left: auto;
    font: 12px var(--mono);
    color: var(--text-faint);
  }
  .n {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  h2 {
    margin: 0 10px 8px;
    font: 600 11px var(--mono);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-faint);
  }
  .tags {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .empty {
    margin: 0 10px;
    color: var(--text-faint);
    font-size: 13px;
  }
  .section {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
  }
  .foot {
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding-top: 12px;
    border-top: 1px solid var(--border);
  }
  .demo {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border-radius: var(--radius-sm);
    background: var(--accent-soft);
    color: var(--accent);
    font-size: 12px;
    font-weight: 600;
  }
  .stats {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 0 10px;
    font: 12px var(--mono);
    color: var(--text-faint);
  }
  .theme {
    justify-content: flex-start;
  }
  .scrim {
    display: none;
  }
  @media (max-width: 900px) {
    aside {
      position: fixed;
      z-index: 40;
      inset: 0 auto 0 0;
      transform: translateX(-100%);
      transition: transform 0.2s ease;
      box-shadow: var(--shadow);
    }
    aside.open {
      transform: none;
    }
    .scrim {
      display: block;
      position: fixed;
      z-index: 39;
      inset: 0;
      border: none;
      background: var(--scrim);
      animation: fade-in 0.2s;
    }
  }
</style>
