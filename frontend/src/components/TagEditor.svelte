<script lang="ts">
  import Icon from './Icon.svelte';

  let { tags, suggestions, onchange }: { tags: string[]; suggestions: string[]; onchange: (tags: string[]) => void } = $props();
  let draft = $state('');
  const listId = `tags-${Math.random().toString(36).slice(2, 8)}`;

  function commit() {
    const t = draft.trim().toLowerCase().replace(/\s+/g, '-');
    draft = '';
    if (t && !tags.includes(t)) onchange([...tags, t]);
  }

  function onkey(e: KeyboardEvent) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      commit();
    } else if (e.key === 'Backspace' && !draft && tags.length) {
      onchange(tags.slice(0, -1));
    }
  }
</script>

<div class="editor">
  {#each tags as t (t)}
    <span class="tag">
      <Icon name="tag" size={12} />{t}
      <button type="button" aria-label={`Rimuovi etichetta ${t}`} onclick={() => onchange(tags.filter((x) => x !== t))}>
        <Icon name="x" size={12} stroke={2.2} />
      </button>
    </span>
  {/each}
  <input
    list={listId}
    bind:value={draft}
    onkeydown={onkey}
    onblur={commit}
    placeholder={tags.length ? 'Aggiungi…' : 'Aggiungi un’etichetta e premi Invio'}
    aria-label="Nuova etichetta"
  />
  <datalist id={listId}>
    {#each suggestions.filter((s) => !tags.includes(s)) as s}<option value={s}></option>{/each}
  </datalist>
</div>

<style>
  .editor {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
    padding: 6px;
    background: var(--bg);
    border: 1px solid var(--border-strong);
    border-radius: var(--radius-sm);
  }
  .editor:focus-within {
    border-color: var(--cyan);
  }
  .tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    height: 24px;
    padding: 0 4px 0 8px;
    border-radius: 999px;
    background: var(--accent-soft);
    color: var(--accent);
    font-size: 12.5px;
    font-weight: 500;
  }
  .tag button {
    display: grid;
    place-items: center;
    width: 18px;
    height: 18px;
    padding: 0;
    border: none;
    border-radius: 50%;
    background: transparent;
    color: inherit;
  }
  .tag button:hover {
    background: var(--accent-soft);
  }
  input {
    flex: 1;
    min-width: 120px;
    height: 24px;
    border: none;
    outline: none;
    background: transparent;
    font-size: 13px;
  }
</style>
