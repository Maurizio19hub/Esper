<script lang="ts">
  import { onMount } from 'svelte';
  import { app } from '../lib/store.svelte';
  import { KIND_LABEL, formatDate, formatSize } from '../lib/format';
  import { queryTerms, renderMarkdown } from '../lib/text';
  import Highlight from './Highlight.svelte';
  import Icon from './Icon.svelte';
  import StatusBadge from './StatusBadge.svelte';
  import TagEditor from './TagEditor.svelte';

  const d = $derived(app.detail);
  const terms = $derived(queryTerms(app.query));
  let confirming = $state(false);
  let closeBtn: HTMLButtonElement;

  onMount(() => closeBtn?.focus());

  const fullText = $derived(d ? d.chunks.map((c) => c.text).join('\n\n') : '');
  const SOURCE: Record<string, string> = { text: 'testo', ocr: 'OCR', visual: 'descrizione visiva' };
</script>

<button class="scrim" aria-label="Chiudi dettaglio" onclick={() => app.closeDoc()}></button>
<div class="panel" role="dialog" aria-modal="true" aria-labelledby="dp-title">
  <header>
    <h2 id="dp-title">{d?.name ?? 'Caricamento…'}</h2>
    <button bind:this={closeBtn} class="icon-btn" aria-label="Chiudi" onclick={() => app.closeDoc()}><Icon name="x" /></button>
  </header>

  {#if !d}
    <div class="loading"><Icon name="loader" size={24} spin /></div>
  {:else}
    <div class="scroll">
      <section class="preview">
        {#if d.kind === 'image' && d.fileUrl}
          <img src={d.fileUrl} alt={`Anteprima di ${d.name}`} />
        {:else if d.kind === 'pdf' && d.fileUrl}
          <iframe src={d.fileUrl} title={`Anteprima di ${d.name}`}></iframe>
        {:else if d.kind === 'markdown' && d.chunks.length}
          <article class="doc md">{@html renderMarkdown(fullText)}</article>
        {:else if d.chunks.length}
          <article class="doc plain">
            {#each d.chunks as c (c.id)}
              <p>{#if c.page}<span class="pg">pagina {c.page}</span>{/if}<Highlight text={c.text} {terms} /></p>
            {/each}
          </article>
        {:else}
          <p class="nopreview">Anteprima non ancora disponibile.</p>
        {/if}
      </section>

      <section class="block">
        <div class="status-row">
          <StatusBadge doc={d} />
          {#if d.error}<p class="err">{d.error}</p>{/if}
        </div>
        <dl>
          <div><dt>Tipo</dt><dd>{KIND_LABEL[d.kind]}</dd></div>
          <div><dt>Dimensione</dt><dd>{formatSize(d.size)}</dd></div>
          {#if d.pages}<div><dt>Pagine</dt><dd>{d.pages}</dd></div>{/if}
          <div><dt>Frammenti</dt><dd>{d.chunkCount}</dd></div>
          <div class="wide"><dt>Aggiunto</dt><dd>{formatDate(d.createdAt)}</dd></div>
        </dl>
      </section>

      <section class="block">
        <h3>Etichette</h3>
        <TagEditor tags={d.tags} suggestions={app.tagList.map((t) => t.name)} onchange={(tags) => app.setTags(d.id, tags)} />
      </section>

      {#if d.chunks.length}
        <section class="block">
          <h3>Frammenti indicizzati <span class="n">{d.chunks.length}</span></h3>
          <p class="hint">Ogni frammento ha un proprio embedding: la ricerca confronta la tua descrizione con questi pezzi.</p>
          <ol>
            {#each d.chunks as c (c.id)}
              <li>
                <span class="meta">#{c.index + 1}{c.page ? ` · p. ${c.page}` : ''} · {SOURCE[c.source]}</span>
                <Highlight text={c.text} {terms} />
              </li>
            {/each}
          </ol>
        </section>
      {/if}
    </div>

    <footer>
      {#if d.fileUrl}
        <a class="btn" href={d.fileUrl} target="_blank" rel="noopener"><Icon name="external" /> Apri file</a>
      {/if}
      <span class="grow"></span>
      {#if confirming}
        <button class="btn btn-ghost" onclick={() => (confirming = false)}>Annulla</button>
        <button class="btn btn-danger" onclick={() => app.removeDoc(d.id)}><Icon name="trash" /> Conferma eliminazione</button>
      {:else}
        <button class="btn btn-ghost btn-danger" onclick={() => (confirming = true)}><Icon name="trash" /> Elimina</button>
      {/if}
    </footer>
  {/if}
</div>

<style>
  .scrim {
    position: fixed;
    z-index: 50;
    inset: 0;
    border: none;
    background: var(--scrim);
    animation: fade-in 0.2s;
  }
  .panel {
    position: fixed;
    z-index: 51;
    top: 0;
    right: 0;
    bottom: 0;
    display: flex;
    flex-direction: column;
    width: min(540px, 100vw);
    background: var(--bg-elev);
    border-left: 1px solid var(--border-strong);
    box-shadow: var(--shadow);
    animation: slide-in 0.22s ease both;
  }
  header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 14px 16px;
    border-bottom: 1px solid var(--border);
  }
  h2 {
    flex: 1;
    font-size: 16px;
    word-break: break-word;
  }
  .loading {
    display: grid;
    place-items: center;
    flex: 1;
    color: var(--text-dim);
  }
  .scroll {
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
  }
  .preview {
    background: var(--bg);
    border-bottom: 1px solid var(--border);
    max-height: 340px;
    overflow: auto;
  }
  .preview img,
  iframe {
    display: block;
    width: 100%;
    height: 320px;
    border: none;
  }
  .preview img {
    object-fit: contain;
    background: var(--bg);
  }
  .doc {
    padding: 18px 22px;
    font-size: 13.5px;
    line-height: 1.65;
  }
  .doc.plain p {
    margin-bottom: 12px;
    white-space: pre-wrap;
  }
  .pg {
    display: block;
    margin-bottom: 4px;
    font: 600 10.5px var(--mono);
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-faint);
  }
  .md :global(h1) {
    font-size: 20px;
    margin: 0 0 10px;
  }
  .md :global(h2) {
    font-size: 16px;
    margin: 18px 0 8px;
  }
  .md :global(p) {
    margin: 0 0 10px;
  }
  .md :global(ul),
  .md :global(ol) {
    margin: 0 0 10px;
    padding-left: 20px;
  }
  .md :global(code) {
    font-family: var(--mono);
    background: var(--bg-hover);
    padding: 1px 5px;
    border-radius: 4px;
  }
  .nopreview {
    padding: 28px;
    text-align: center;
    color: var(--text-faint);
  }
  .block {
    padding: 16px 18px;
    border-bottom: 1px solid var(--border);
  }
  h3 {
    margin-bottom: 10px;
    font: 600 11px var(--mono);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--text-faint);
  }
  .n {
    margin-left: 6px;
    color: var(--accent);
  }
  .status-row {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
  }
  .err {
    color: var(--err);
    font-size: 13px;
  }
  dl {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 0;
  }
  dl .wide {
    grid-column: 1 / -1;
  }
  dt {
    font-size: 11.5px;
    color: var(--text-faint);
  }
  dd {
    margin: 0;
    font-weight: 500;
  }
  .hint {
    margin-bottom: 10px;
    color: var(--text-faint);
    font-size: 12.5px;
  }
  ol {
    list-style: none;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  li {
    padding: 10px 12px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    font-size: 13px;
    color: var(--text-dim);
  }
  .meta {
    display: block;
    margin-bottom: 4px;
    font: 11px var(--mono);
    color: var(--text-faint);
  }
  footer {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    border-top: 1px solid var(--border);
  }
  .grow {
    flex: 1;
  }
  a.btn {
    text-decoration: none;
    color: var(--text);
  }
</style>
