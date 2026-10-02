// Utilità di testo condivise: normalizzazione, termini di ricerca, evidenziazione.

const STOPWORDS = new Set(
  (
    'il lo la i gli le un uno una di a da in con su per tra fra e o ma che del dello della dei degli delle ' +
    'al allo alla ai agli alle dal dalla dai dalle nel nella nei nelle sul sulla come sono ho ha mi ti si non ' +
    'più questo questa quello quella cerco vorrei trova trovami dove cosa quale quali documenti documento file ' +
    'messo mettere avevo avevi aveva'
  ).split(' '),
);

/** Minuscolo e senza accenti, mantenendo la stessa lunghezza del testo originale. */
export function fold(s: string): string {
  return s.replace(/[\s\S]/gu, (c) => {
    if (c.length > 1) return c;
    const base = c.normalize('NFD')[0] ?? c;
    return base.toLowerCase()[0] ?? base;
  });
}

export function queryTerms(q: string): string[] {
  return fold(q)
    .split(/[^\p{L}\p{N}]+/u)
    .filter((t) => t.length >= 3 && !STOPWORDS.has(t));
}

export interface Segment {
  text: string;
  hit: boolean;
}

/** Spezza `text` in segmenti marcando le occorrenze dei termini (senza HTML). */
export function highlight(text: string, terms: string[]): Segment[] {
  if (!terms.length || !text) return [{ text, hit: false }];
  const pattern = terms.map((t) => t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|');
  const re = new RegExp(pattern, 'gu');
  const folded = fold(text);
  const out: Segment[] = [];
  let last = 0;
  for (const m of folded.matchAll(re)) {
    const start = m.index ?? 0;
    if (m[0].length === 0) continue;
    if (start > last) out.push({ text: text.slice(last, start), hit: false });
    out.push({ text: text.slice(start, start + m[0].length), hit: true });
    last = start + m[0].length;
  }
  if (last < text.length) out.push({ text: text.slice(last), hit: false });
  return out.length ? out : [{ text, hit: false }];
}

/** Divide il testo in chunk di circa `max` caratteri rispettando i paragrafi. */
export function chunkText(text: string, max = 420): string[] {
  const paragraphs = text
    .split(/\n{2,}/)
    .map((p) => p.trim())
    .filter(Boolean);
  const chunks: string[] = [];
  let current = '';
  for (const p of paragraphs) {
    if (current && current.length + p.length + 2 > max) {
      chunks.push(current);
      current = '';
    }
    if (p.length > max) {
      for (const sentence of p.split(/(?<=[.!?])\s+/)) {
        if (current && current.length + sentence.length + 1 > max) {
          chunks.push(current);
          current = '';
        }
        current = current ? `${current} ${sentence}` : sentence;
      }
    } else {
      current = current ? `${current}\n\n${p}` : p;
    }
  }
  if (current) chunks.push(current);
  return chunks;
}

function escapeHtml(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

/** Mini renderer Markdown. Il testo viene prima escapato: l'HTML prodotto contiene solo i nostri tag. */
export function renderMarkdown(src: string): string {
  const lines = escapeHtml(src).split('\n');
  const html: string[] = [];
  let list: 'ul' | 'ol' | null = null;
  const closeList = () => {
    if (list) html.push(`</${list}>`);
    list = null;
  };
  const inline = (s: string) =>
    s
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, '$1<em>$2</em>');
  for (const line of lines) {
    let m: RegExpMatchArray | null;
    if ((m = line.match(/^(#{1,3})\s+(.*)$/))) {
      closeList();
      const level = m[1]!.length;
      html.push(`<h${level}>${inline(m[2]!)}</h${level}>`);
    } else if ((m = line.match(/^\s*[-*]\s+(.*)$/))) {
      if (list !== 'ul') {
        closeList();
        html.push('<ul>');
        list = 'ul';
      }
      html.push(`<li>${inline(m[1]!)}</li>`);
    } else if ((m = line.match(/^\s*\d+[.)]\s+(.*)$/))) {
      if (list !== 'ol') {
        closeList();
        html.push('<ol>');
        list = 'ol';
      }
      html.push(`<li>${inline(m[1]!)}</li>`);
    } else if (line.trim() === '') {
      closeList();
    } else {
      closeList();
      html.push(`<p>${inline(line)}</p>`);
    }
  }
  closeList();
  return html.join('\n');
}
