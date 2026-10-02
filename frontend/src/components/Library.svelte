<script lang="ts">
  import { app } from '../lib/store.svelte';
  import { ACCEPT } from '../lib/format';
  import DocCard from './DocCard.svelte';
  import Icon from './Icon.svelte';

  let picker: HTMLInputElement;
</script>

<div class="head">
  <div>
    <h1>{app.activeTags.length ? 'Documenti filtrati' : 'Libreria'}</h1>
    {#if app.activeTags.length}
      <div class="filters">
        {#each app.activeTags as t}
          <button class="chip active" onclick={() => app.toggleTag(t)} aria-label={`Rimuovi filtro ${t}`}>
            {t} <Icon name="x" size={12} stroke={2.2} />
          </button>
        {/each}
        <button class="btn btn-ghost small" onclick={() => app.clearFilters()}>Azzera filtri</button>
      </div>
    {/if}
  </div>
  <div class="tools">
    <label class="sort">
      <span class="sr-only">Ordina per</span>
      <select value={app.sort} onchange={(e) => app.setSort(e.currentTarget.value as 'recent' | 'name' | 'size')}>
        <option value="recent">Più recenti</option>
        <option value="name">Nome</option>
        <option value="size">Dimensione</option>
      </select>
    </label>
    <div class="seg" role="group" aria-label="Vista">
      <button class:on={app.view === 'grid'} aria-pressed={app.view === 'grid'} aria-label="Vista a griglia" onclick={() => app.setView('grid')}><Icon name="grid" /></button>
      <button class:on={app.view === 'list'} aria-pressed={app.view === 'list'} aria-label="Vista a elenco" onclick={() => app.setView('list')}><Icon name="list" /></button>
    </div>
  </div>
</div>

{#if app.loading}
  <div class="grid">
    {#each Array(8) as _}<div class="skeleton"></div>{/each}
  </div>
{:else if app.loadError}
  <div class="state">
    <Icon name="alert" size={28} />
    <h2>Impossibile caricare i documenti</h2>
    <p>{app.loadError}</p>
    <button class="btn" onclick={() => app.refresh()}>Riprova</button>
  </div>
{:else if app.sortedDocs.length === 0}
  <div class="state empty">
    <div class="orb"><Icon name="upload" size={30} /></div>
    <h2>{app.activeTags.length ? 'Nessun documento con queste etichette' : 'La tua libreria è vuota'}</h2>
    <p>
      {app.activeTags.length
        ? 'Prova a togliere qualche filtro.'
        : 'Trascina qui i tuoi file: PDF, immagini, Markdown o testo. Esper li leggerà e li renderà ricercabili per significato.'}
    </p>
    {#if !app.activeTags.length}
      <button class="btn btn-primary" onclick={() => picker.click()}><Icon name="plus" /> Aggiungi file</button>
    {:else}
      <button class="btn" onclick={() => app.clearFilters()}>Azzera filtri</button>
    {/if}
  </div>
{:else if app.view === 'grid'}
  <div class="grid">
    {#each app.sortedDocs as doc (doc.id)}<DocCard {doc} view="grid" />{/each}
  </div>
{:else}
  <div class="list">
    {#each app.sortedDocs as doc (doc.id)}<DocCard {doc} view="list" />{/each}
  </div>
{/if}

<input bind:this={picker} type="file" multiple accept={ACCEPT} hidden onchange={(e) => { void app.addFiles([...(e.currentTarget.files ?? [])]); e.currentTarget.value = ''; }} />

<style>
  .head {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 18px;
    flex-wrap: wrap;
  }
  h1 {
    font-size: 22px;
    letter-spacing: -0.01em;
  }
  .filters {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    margin-top: 8px;
  }
  .chip.active {
    background: var(--cyan-soft);
    color: var(--cyan);
    border: none;
    cursor: pointer;
  }
  .small {
    height: 26px;
    padding: 0 8px;
    font-size: 12px;
  }
  .tools {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  select {
    height: 34px;
    padding: 0 10px;
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-sm);
    background: var(--bg-elev-2);
  }
  .seg {
    display: flex;
    padding: 2px;
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-sm);
    background: var(--bg-elev-2);
  }
  .seg button {
    display: grid;
    place-items: center;
    width: 32px;
    height: 28px;
    border: none;
    border-radius: 6px;
    background: transparent;
    color: var(--text-faint);
  }
  .seg button.on {
    background: var(--accent-soft);
    color: var(--accent);
  }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 16px;
  }
  .list {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }
  .skeleton {
    height: 260px;
    border-radius: var(--radius);
    background: var(--bg-elev);
    border: 1px solid var(--border);
    animation: pulse 1.4s ease-in-out infinite;
  }
  .state {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    margin: 8vh auto 0;
    max-width: 440px;
    text-align: center;
    color: var(--text-dim);
  }
  .state h2 {
    color: var(--text);
    font-size: 19px;
  }
  .state .btn {
    margin-top: 8px;
  }
  .orb {
    display: grid;
    place-items: center;
    width: 76px;
    height: 76px;
    border-radius: 50%;
    color: var(--accent);
    background: radial-gradient(circle, var(--accent-soft), transparent 70%);
    border: 1px dashed var(--accent);
  }
</style>
