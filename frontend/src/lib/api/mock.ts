// API simulata: dati in memoria, pipeline di elaborazione finta e ricerca "semantica" a sinonimi.
import type { Chunk, ChunkSource, Doc, DocDetail, DocKind, EsperApi, MatchVia, SearchHit, SearchMatch, TagCount } from '../types';
import { chunkText, fold, queryTerms } from '../text';
import { detectKind } from '../format';
import { SEED } from './seed';

/** Gruppi di concetti: simulano la vicinanza semantica degli embedding. */
const CONCEPTS: Record<string, string[]> = {
  casa: ['casa', 'appartament', 'affitt', 'locazion', 'canone', 'locator', 'conduttor', 'immobil', 'condomini', 'abitativ'],
  cibo: ['ricett', 'dolce', 'cucin', 'mascarpone', 'ingredient', 'tiramis', 'forno', 'pranzo', 'cena', 'mangiare', 'caffe', 'cuocere'],
  ai: ['neural', 'machine learning', 'apprendiment', 'intelligenza artificiale', 'modell', 'embedding', 'transformer', 'addestr', 'vettorial', 'backprop'],
  soldi: ['fattur', 'spese', 'spesa', 'bilancio', 'pagament', 'costo', 'euro', 'iva', 'budget', 'risparmi', 'importo', 'denaro', 'soldi', 'bonifico'],
  mare: ['mare', 'spiaggia', 'tramonto', 'sardegna', 'costa', 'onda', 'sole', 'orizzonte', 'vacanz', 'scogliera'],
  salute: ['medic', 'visita', 'salute', 'dottor', 'cardiolog', 'analisi', 'terapia', 'pressione arteriosa', 'elettrocardiogramma', 'referto'],
  viaggio: ['viaggio', 'lisbona', 'portogallo', 'hotel', 'volo', 'tram', 'turist', 'itinerario', 'belem', 'sintra'],
  impianto: ['impianto', 'elettric', 'caldaia', 'idraulic', 'tubatur', 'riscaldament', 'termostat', 'manutenzion', 'quadro', 'rubinetto', 'differenziale'],
  libri: ['borges', 'bibliotec', 'libro', 'libri', 'letteratur', 'romanzo', 'racconto', 'scrittore', 'babele'],
  sport: ['allenament', 'corsa', 'correre', 'palestra', 'sport', 'esercizi', 'maratona', 'fitness', 'ripetute'],
  software: ['bug', 'login', 'errore', 'schermata', 'applicazion', 'password', 'accesso', 'software', 'credenziali'],
  animali: ['gatto', 'gatti', 'felino', 'cane', 'animale', 'animali', 'divano'],
  lavoro: ['trimestre', 'ricavi', 'margine', 'azienda', 'relazione', 'fatturato', 'prodotti'],
};

function conceptsOf(foldedText: string): Set<string> {
  const out = new Set<string>();
  for (const [name, stems] of Object.entries(CONCEPTS)) {
    if (stems.some((s) => foldedText.includes(s))) out.add(name);
  }
  return out;
}

interface Rec {
  doc: Doc;
  chunks: Chunk[];
  folded: string[];
  concepts: Set<string>[];
  file?: File;
  /** Esito simulato dell'elaborazione, deciso alla creazione. */
  plan?: { chunks: { text: string; page?: number; source: ChunkSource }[]; error?: string };
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));
const latency = () => sleep(50 + Math.random() * 110);
const normTag = (t: string) => t.trim().toLowerCase().replace(/\s+/g, '-');

class MockApi implements EsperApi {
  mode = 'mock' as const;
  private recs = new Map<number, Rec>();
  private listeners = new Set<() => void>();
  private nextId = 1;
  private nextChunkId = 1;
  private queue: Promise<void> = Promise.resolve();

  constructor() {
    for (const s of SEED) {
      const id = this.nextId++;
      const created = new Date(Date.now() - s.daysAgo * 864e5 - Math.floor(Math.random() * 6) * 36e5).toISOString();
      const chunkInputs: { text: string; page?: number; source: ChunkSource }[] = [];
      if (s.pagesText) s.pagesText.forEach((t, i) => chunkInputs.push({ text: t, page: i + 1, source: 'text' }));
      if (s.text) chunkText(s.text).forEach((t) => chunkInputs.push({ text: t, source: 'text' }));
      if (s.ocr) chunkInputs.push({ text: s.ocr, source: 'ocr' });
      if (s.visual) chunkInputs.push({ text: s.visual, source: 'visual' });
      const art = s.art?.();
      const doc: Doc = {
        id,
        name: s.name,
        kind: s.kind,
        mime: mimeOf(s.kind),
        size: s.size,
        status: s.status ?? 'indexed',
        progress: 0,
        error: s.error,
        tags: [...s.tags],
        createdAt: created,
        pages: s.pages,
        chunkCount: 0,
        excerpt: (chunkInputs[0]?.text ?? '').replace(/\s+/g, ' ').slice(0, 180),
        thumbnailUrl: art,
        fileUrl: art,
      };
      const rec: Rec = { doc, chunks: [], folded: [], concepts: [] };
      if (doc.status === 'indexed') this.setChunks(rec, chunkInputs);
      else if (doc.status === 'queued') rec.plan = { chunks: chunkInputs };
      this.recs.set(id, rec);
      if (doc.status === 'queued') setTimeout(() => this.enqueue(id), 2500);
    }
  }

  private setChunks(rec: Rec, inputs: { text: string; page?: number; source: ChunkSource }[]) {
    rec.chunks = inputs.map((c, i) => ({ id: this.nextChunkId++, index: i, page: c.page, text: c.text, source: c.source }));
    rec.folded = rec.chunks.map((c) => fold(c.text));
    rec.concepts = rec.folded.map(conceptsOf);
    rec.doc.chunkCount = rec.chunks.length;
    if (!rec.doc.excerpt && rec.chunks[0]) rec.doc.excerpt = rec.chunks[0].text.replace(/\s+/g, ' ').slice(0, 180);
  }

  private emit() {
    this.listeners.forEach((cb) => cb());
  }

  private enqueue(id: number) {
    this.queue = this.queue.then(() => this.process(id)).catch(() => {});
  }

  private async process(id: number) {
    const rec = this.recs.get(id);
    if (!rec) return;
    rec.doc.status = 'processing';
    rec.doc.progress = 0.05;
    this.emit();
    for (const p of [0.2, 0.4, 0.65, 0.85]) {
      await sleep(350 + Math.random() * 450);
      if (!this.recs.has(id)) return;
      rec.doc.progress = p;
      this.emit();
    }
    await sleep(250);
    if (!this.recs.has(id)) return;
    const plan = rec.plan;
    if (!plan || plan.error || plan.chunks.length === 0) {
      rec.doc.status = 'error';
      rec.doc.error = plan?.error ?? 'Nessun testo estraibile da questo file.';
    } else {
      this.setChunks(rec, plan.chunks);
      rec.doc.status = 'indexed';
      rec.doc.error = undefined;
    }
    rec.doc.progress = 1;
    rec.plan = undefined;
    this.emit();
  }

  private async planFor(file: File, kind: DocKind): Promise<Rec['plan']> {
    if (kind === 'markdown' || kind === 'text') {
      const text = await file.text();
      if (!text.trim()) return { chunks: [], error: 'Il file è vuoto.' };
      return { chunks: chunkText(text).map((t) => ({ text: t, source: 'text' as const })) };
    }
    if (kind === 'image') {
      return { chunks: [{ text: `Immagine «${file.name}»: analisi visiva simulata. Nella versione reale qui compare il testo OCR e la descrizione generata da SigLIP.`, source: 'visual' }] };
    }
    return {
      chunks: [{ text: `Testo estratto dal PDF «${file.name}» (simulazione). Nella versione reale qui compare il contenuto vero del documento, pagina per pagina.`, page: 1, source: 'text' }],
    };
  }

  async listDocuments(params?: { tags?: string[] }): Promise<Doc[]> {
    await latency();
    const tags = params?.tags ?? [];
    return [...this.recs.values()]
      .map((r) => r.doc)
      .filter((d) => tags.every((t) => d.tags.includes(t)))
      .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
      .map(cloneDoc);
  }

  async getDocument(id: number): Promise<DocDetail> {
    await latency();
    const rec = this.recs.get(id);
    if (!rec) throw new Error('Documento non trovato');
    return { ...cloneDoc(rec.doc), chunks: rec.chunks.map((c) => ({ ...c })) };
  }

  async uploadDocuments(files: File[]): Promise<Doc[]> {
    await latency();
    const created: Doc[] = [];
    for (const file of files) {
      const kind = detectKind(file.name, file.type);
      if (!kind) continue;
      const id = this.nextId++;
      const url = URL.createObjectURL(file);
      const doc: Doc = {
        id,
        name: file.name,
        kind,
        mime: file.type || mimeOf(kind),
        size: file.size,
        status: 'queued',
        progress: 0,
        tags: [],
        createdAt: new Date().toISOString(),
        chunkCount: 0,
        excerpt: '',
        pages: kind === 'pdf' ? Math.max(1, Math.round(file.size / 60_000)) : undefined,
        thumbnailUrl: kind === 'image' ? url : undefined,
        fileUrl: url,
      };
      const rec: Rec = { doc, chunks: [], folded: [], concepts: [], file };
      rec.plan = await this.planFor(file, kind);
      if (rec.plan?.chunks[0]) doc.excerpt = rec.plan.chunks[0].text.replace(/\s+/g, ' ').slice(0, 180);
      this.recs.set(id, rec);
      this.enqueue(id);
      created.push(cloneDoc(doc));
    }
    this.emit();
    return created;
  }

  async updateTags(id: number, tags: string[]): Promise<Doc> {
    await latency();
    const rec = this.recs.get(id);
    if (!rec) throw new Error('Documento non trovato');
    rec.doc.tags = [...new Set(tags.map(normTag).filter(Boolean))];
    return cloneDoc(rec.doc);
  }

  async deleteDocument(id: number): Promise<void> {
    await latency();
    const rec = this.recs.get(id);
    if (rec?.file && rec.doc.fileUrl) URL.revokeObjectURL(rec.doc.fileUrl);
    this.recs.delete(id);
    this.emit();
  }

  async listTags(): Promise<TagCount[]> {
    await latency();
    const counts = new Map<string, number>();
    for (const { doc } of this.recs.values()) for (const t of doc.tags) counts.set(t, (counts.get(t) ?? 0) + 1);
    return [...counts].map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count || a.name.localeCompare(b.name));
  }

  async search(query: string, params?: { tags?: string[] }): Promise<SearchHit[]> {
    await sleep(180 + Math.random() * 220);
    const terms = queryTerms(query);
    const qConcepts = conceptsOf(fold(query));
    if (!terms.length && !qConcepts.size) return [];
    const tags = params?.tags ?? [];
    const hits: SearchHit[] = [];
    for (const rec of this.recs.values()) {
      const { doc } = rec;
      if (doc.status !== 'indexed' || !tags.every((t) => doc.tags.includes(t))) continue;
      const matches: SearchMatch[] = [];
      rec.chunks.forEach((chunk, i) => {
        const folded = rec.folded[i]!;
        const lex = terms.length ? terms.filter((t) => folded.includes(t)).length / terms.length : 0;
        const cc = rec.concepts[i]!;
        const sem = qConcepts.size ? [...qConcepts].filter((c) => cc.has(c)).length / qConcepts.size : 0;
        const score = Math.min(0.99, 0.55 * sem + 0.45 * lex + (lex > 0 && sem > 0 ? 0.1 : 0));
        if (score < 0.2) return;
        const via: MatchVia = lex > 0 && sem > 0 ? 'both' : lex > 0 ? 'keyword' : 'semantic';
        matches.push({ chunkId: chunk.id, page: chunk.page, text: chunk.text, score, source: chunk.source, via });
      });
      const meta = fold(`${doc.name} ${doc.tags.join(' ')}`);
      const metaScore = terms.length ? (terms.filter((t) => meta.includes(t)).length / terms.length) * 0.15 : 0;
      if (!matches.length && metaScore === 0) continue;
      matches.sort((a, b) => b.score - a.score);
      const best = matches[0]?.score ?? 0.2;
      hits.push({ doc: cloneDoc(doc), score: Math.min(0.99, best + metaScore), matches: matches.slice(0, 3) });
    }
    return hits.sort((a, b) => b.score - a.score);
  }

  subscribe(cb: () => void): () => void {
    this.listeners.add(cb);
    return () => this.listeners.delete(cb);
  }
}

function mimeOf(kind: DocKind): string {
  return { pdf: 'application/pdf', image: 'image/png', markdown: 'text/markdown', text: 'text/plain' }[kind];
}

function cloneDoc(d: Doc): Doc {
  return { ...d, tags: [...d.tags] };
}

export const mockApi: EsperApi = new MockApi();
