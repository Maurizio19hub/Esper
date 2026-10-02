import { api } from './api';
import { detectKind } from './format';
import type { Doc, DocDetail, SearchHit, TagCount } from './types';

type Theme = 'light' | 'dark';
type View = 'grid' | 'list';
type Sort = 'recent' | 'name' | 'size';

export interface Toast {
  id: number;
  kind: 'info' | 'success' | 'error';
  text: string;
}

function read<T extends string>(key: string, allowed: readonly T[], fallback: T): T {
  try {
    const v = localStorage.getItem(key);
    return allowed.includes(v as T) ? (v as T) : fallback;
  } catch {
    return fallback;
  }
}

function write(key: string, value: string) {
  try {
    localStorage.setItem(key, value);
  } catch {
    /* storage non disponibile: la preferenza resta solo per la sessione */
  }
}

const msg = (e: unknown) => (e instanceof Error ? e.message : String(e));

class AppStore {
  docs = $state<Doc[]>([]);
  tagList = $state<TagCount[]>([]);
  loading = $state(true);
  loadError = $state<string | null>(null);

  query = $state('');
  activeTags = $state<string[]>([]);
  view = $state<View>(read('esper.view', ['grid', 'list'], 'grid'));
  sort = $state<Sort>(read('esper.sort', ['recent', 'name', 'size'], 'recent'));
  theme = $state<Theme>((document.documentElement.dataset.theme as Theme) === 'light' ? 'light' : 'dark');

  hits = $state<SearchHit[]>([]);
  searching = $state(false);
  searchError = $state<string | null>(null);

  selectedId = $state<number | null>(null);
  detail = $state<DocDetail | null>(null);

  toasts = $state<Toast[]>([]);
  sidebarOpen = $state(false);

  isSearching = $derived(this.query.trim().length > 0);
  inflight = $derived(this.docs.filter((d) => d.status === 'queued' || d.status === 'processing').length);
  totalChunks = $derived(this.docs.reduce((n, d) => n + d.chunkCount, 0));
  sortedDocs = $derived.by(() => {
    const list = [...this.docs];
    if (this.sort === 'name') list.sort((a, b) => a.name.localeCompare(b.name, 'it'));
    else if (this.sort === 'size') list.sort((a, b) => b.size - a.size);
    else list.sort((a, b) => b.createdAt.localeCompare(a.createdAt));
    return list;
  });

  private unsubscribe: (() => void) | null = null;
  private refreshSeq = 0;
  private searchSeq = 0;
  private searchTimer: ReturnType<typeof setTimeout> | undefined;
  private toastId = 0;

  async init() {
    this.unsubscribe = api.subscribe(() => void this.refresh());
    await this.refresh();
  }

  destroy() {
    this.unsubscribe?.();
    clearTimeout(this.searchTimer);
  }

  async refresh() {
    const seq = ++this.refreshSeq;
    try {
      const [docs, tags] = await Promise.all([api.listDocuments({ tags: this.activeTags }), api.listTags()]);
      if (seq !== this.refreshSeq) return;
      const finished = this.docs.some((old) => old.status !== 'indexed' && docs.find((d) => d.id === old.id)?.status === 'indexed');
      this.docs = docs;
      this.tagList = tags;
      this.loadError = null;
      if (this.selectedId !== null) {
        if (!docs.some((d) => d.id === this.selectedId) && !this.activeTags.length) this.closeDoc();
        else if (this.detail && this.detail.status !== 'indexed') void this.loadDetail(this.selectedId);
      }
      if (finished && this.isSearching) void this.runSearch();
    } catch (e) {
      this.loadError = msg(e);
    } finally {
      this.loading = false;
    }
  }

  // ---- ricerca -------------------------------------------------------------

  setQuery(q: string) {
    this.query = q;
    clearTimeout(this.searchTimer);
    if (!q.trim()) {
      this.searchSeq++;
      this.hits = [];
      this.searching = false;
      this.searchError = null;
      return;
    }
    this.searching = true;
    this.searchTimer = setTimeout(() => void this.runSearch(), 260);
  }

  async runSearch() {
    const q = this.query.trim();
    if (!q) return;
    const seq = ++this.searchSeq;
    this.searching = true;
    try {
      const hits = await api.search(q, { tags: this.activeTags });
      if (seq !== this.searchSeq) return;
      this.hits = hits;
      this.searchError = null;
    } catch (e) {
      if (seq === this.searchSeq) this.searchError = msg(e);
    } finally {
      if (seq === this.searchSeq) this.searching = false;
    }
  }

  // ---- filtri ----------------------------------------------------------------

  toggleTag(tag: string) {
    this.activeTags = this.activeTags.includes(tag) ? this.activeTags.filter((t) => t !== tag) : [...this.activeTags, tag];
    void this.refresh();
    if (this.isSearching) void this.runSearch();
  }

  clearFilters() {
    this.activeTags = [];
    void this.refresh();
    if (this.isSearching) void this.runSearch();
  }

  setView(v: View) {
    this.view = v;
    write('esper.view', v);
  }

  setSort(s: Sort) {
    this.sort = s;
    write('esper.sort', s);
  }

  toggleTheme() {
    this.theme = this.theme === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = this.theme;
    write('esper.theme', this.theme);
  }

  // ---- documenti -------------------------------------------------------------

  async openDoc(id: number) {
    this.selectedId = id;
    this.detail = null;
    await this.loadDetail(id);
  }

  private async loadDetail(id: number) {
    try {
      const d = await api.getDocument(id);
      if (this.selectedId === id) this.detail = d;
    } catch (e) {
      this.toast('error', msg(e));
      if (this.selectedId === id) this.closeDoc();
    }
  }

  closeDoc() {
    this.selectedId = null;
    this.detail = null;
  }

  async addFiles(files: File[]) {
    const valid = files.filter((f) => detectKind(f.name, f.type));
    const rejected = files.length - valid.length;
    if (rejected) this.toast('error', rejected === 1 ? 'Formato non supportato: file ignorato.' : `${rejected} file con formato non supportato ignorati.`);
    if (!valid.length) return;
    try {
      await api.uploadDocuments(valid);
      this.toast('success', valid.length === 1 ? 'File aggiunto: elaborazione in corso.' : `${valid.length} file aggiunti: elaborazione in corso.`);
      await this.refresh();
    } catch (e) {
      this.toast('error', `Caricamento non riuscito: ${msg(e)}`);
    }
  }

  async setTags(id: number, tags: string[]) {
    try {
      const updated = await api.updateTags(id, tags);
      if (this.detail?.id === id) this.detail = { ...this.detail, tags: updated.tags };
      await this.refresh();
      if (this.isSearching) void this.runSearch();
    } catch (e) {
      this.toast('error', msg(e));
    }
  }

  async removeDoc(id: number) {
    try {
      await api.deleteDocument(id);
      if (this.selectedId === id) this.closeDoc();
      this.hits = this.hits.filter((h) => h.doc.id !== id);
      this.toast('info', 'Documento eliminato.');
      await this.refresh();
    } catch (e) {
      this.toast('error', msg(e));
    }
  }

  // ---- notifiche ---------------------------------------------------------------

  toast(kind: Toast['kind'], text: string) {
    const id = ++this.toastId;
    this.toasts = [...this.toasts, { id, kind, text }];
    setTimeout(() => this.dismissToast(id), 4500);
  }

  dismissToast(id: number) {
    this.toasts = this.toasts.filter((t) => t.id !== id);
  }
}

export const app = new AppStore();
export const apiMode = api.mode;
