<script lang="ts">
  import { app } from '../lib/store.svelte';
  import Icon from './Icon.svelte';
</script>

<div class="stack" aria-live="polite">
  {#each app.toasts as t (t.id)}
    <div class="toast {t.kind}" role="status">
      <Icon name={t.kind === 'error' ? 'alert' : t.kind === 'success' ? 'check' : 'sparkle'} size={16} />
      <span>{t.text}</span>
      <button class="icon-btn" aria-label="Chiudi notifica" onclick={() => app.dismissToast(t.id)}><Icon name="x" size={14} /></button>
    </div>
  {/each}
</div>

<style>
  .stack {
    position: fixed;
    z-index: 100;
    right: 18px;
    bottom: 18px;
    display: flex;
    flex-direction: column;
    gap: 8px;
    max-width: calc(100vw - 36px);
  }
  .toast {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 8px 10px 14px;
    min-width: 260px;
    max-width: 420px;
    background: var(--bg-elev-2);
    border: 1px solid var(--border-strong);
    border-left: 3px solid var(--cyan);
    border-radius: var(--radius-sm);
    box-shadow: var(--shadow);
    animation: rise 0.25s ease both;
  }
  .toast span {
    flex: 1;
  }
  .success {
    border-left-color: var(--ok);
  }
  .error {
    border-left-color: var(--err);
  }
  .toast .icon-btn {
    width: 26px;
    height: 26px;
  }
</style>
