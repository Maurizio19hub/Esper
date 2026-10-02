<script lang="ts">
  import { onMount } from 'svelte';
  import { app } from './lib/store.svelte';
  import { ACCEPT } from './lib/format';
  import DetailPanel from './components/DetailPanel.svelte';
  import Icon from './components/Icon.svelte';
  import Library from './components/Library.svelte';
  import SearchBar from './components/SearchBar.svelte';
  import SearchResults from './components/SearchResults.svelte';
  import Sidebar from './components/Sidebar.svelte';
  import Toasts from './components/Toasts.svelte';

  let picker: HTMLInputElement;
  let dragDepth = $state(0);

  onMount(() => {
    void app.init();
    const q = new URLSearchParams(location.search).get('q');
    if (q) app.setQuery(q);
    return () => app.destroy();
  });

  const hasFiles = (e: DragEvent) => !!e.dataTransfer?.types.includes('Files');

  function onkeydown(e: KeyboardEvent) {
    const el = e.target as HTMLElement | null;
    const typing = el && (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA' || el.isContentEditable);
    if (e.key === '/' && !typing && !e.metaKey && !e.ctrlKey) {
      e.preventDefault();
      document.getElementById('search')?.focus();
    } else if (e.key === 'Escape') {
      if (app.selectedId !== null) app.closeDoc();
      else if (app.sidebarOpen) app.sidebarOpen = false;
    }
  }
</script>

<svelte:window
  {onkeydown}
  ondragenter={(e) => {
    if (hasFiles(e)) {
      e.preventDefault();
      dragDepth++;
    }
  }}
  ondragover={(e) => hasFiles(e) && e.preventDefault()}
  ondragleave={(e) => hasFiles(e) && (dragDepth = Math.max(0, dragDepth - 1))}
  ondrop={(e) => {
    if (!hasFiles(e)) return;
    e.preventDefault();
    dragDepth = 0;
    void app.addFiles([...(e.dataTransfer?.files ?? [])]);
  }}
/>

<div class="shell">
  <Sidebar />
  <main>
    <header>
      <button class="icon-btn menu" aria-label="Apri menu" onclick={() => (app.sidebarOpen = true)}><Icon name="menu" /></button>
      <SearchBar />
      <button class="btn btn-primary" onclick={() => picker.click()}><Icon name="plus" /> <span class="lbl">Aggiungi file</span></button>
      {#if app.inflight > 0}
        <span class="busy" title="Documenti in elaborazione"><Icon name="loader" size={16} spin /> {app.inflight}</span>
      {/if}
    </header>
    <div class="content">
      {#if app.isSearching}
        <SearchResults />
      {:else}
        <Library />
      {/if}
    </div>
  </main>

  {#if app.selectedId !== null}<DetailPanel />{/if}
  <Toasts />

  {#if dragDepth > 0}
    <div class="drop" aria-hidden="true">
      <div class="drop-inner">
        <Icon name="upload" size={42} stroke={1.5} />
        <strong>Rilascia per aggiungere a Esper</strong>
        <span>PDF, immagini (JPG, PNG), Markdown e testo</span>
      </div>
    </div>
  {/if}
</div>

<input bind:this={picker} type="file" multiple accept={ACCEPT} hidden onchange={(e) => { void app.addFiles([...(e.currentTarget.files ?? [])]); e.currentTarget.value = ''; }} />

<style>
  .shell {
    display: flex;
    height: 100%;
  }
  main {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
  }
  header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 14px 24px;
    border-bottom: 1px solid var(--border);
    background: color-mix(in srgb, var(--bg) 88%, transparent);
    backdrop-filter: blur(8px);
  }
  .content {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
  }
  .menu {
    display: none;
  }
  .busy {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font: 12px var(--mono);
    color: var(--cyan);
  }
  .drop {
    position: fixed;
    z-index: 200;
    inset: 0;
    display: grid;
    place-items: center;
    background: color-mix(in srgb, var(--bg) 80%, transparent);
    backdrop-filter: blur(4px);
    animation: fade-in 0.15s;
    pointer-events: none;
  }
  .drop-inner {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 56px 72px;
    border: 2px dashed var(--accent);
    border-radius: 24px;
    background: var(--bg-elev);
    color: var(--accent);
    text-align: center;
  }
  .drop-inner strong {
    font-size: 18px;
    color: var(--text);
  }
  .drop-inner span {
    color: var(--text-dim);
  }
  @media (max-width: 900px) {
    .menu {
      display: grid;
    }
    header {
      padding: 12px 14px;
    }
    .content {
      padding: 16px 14px;
    }
    .lbl {
      display: none;
    }
  }
</style>
