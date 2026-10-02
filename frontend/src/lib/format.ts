import type { DocKind, DocStatus } from './types';

export function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 ** 2) return `${(bytes / 1024).toFixed(0)} KB`;
  if (bytes < 1024 ** 3) return `${(bytes / 1024 ** 2).toFixed(1).replace('.', ',')} MB`;
  return `${(bytes / 1024 ** 3).toFixed(1).replace('.', ',')} GB`;
}

const rtf = new Intl.RelativeTimeFormat('it', { numeric: 'auto' });

export function formatRelative(iso: string): string {
  const diff = new Date(iso).getTime() - Date.now();
  const abs = Math.abs(diff);
  const min = 60_000;
  if (abs < min) return 'adesso';
  if (abs < 60 * min) return rtf.format(Math.round(diff / min), 'minute');
  if (abs < 24 * 60 * min) return rtf.format(Math.round(diff / (60 * min)), 'hour');
  if (abs < 30 * 24 * 60 * min) return rtf.format(Math.round(diff / (24 * 60 * min)), 'day');
  return new Date(iso).toLocaleDateString('it-IT', { day: 'numeric', month: 'short', year: 'numeric' });
}

export function formatDate(iso: string): string {
  return new Date(iso).toLocaleString('it-IT', { day: 'numeric', month: 'long', year: 'numeric', hour: '2-digit', minute: '2-digit' });
}

export const KIND_LABEL: Record<DocKind, string> = {
  pdf: 'PDF',
  image: 'Immagine',
  markdown: 'Markdown',
  text: 'Testo',
};

export const KIND_SHORT: Record<DocKind, string> = { pdf: 'PDF', image: 'IMG', markdown: 'MD', text: 'TXT' };

export const STATUS_LABEL: Record<DocStatus, string> = {
  queued: 'In coda',
  processing: 'Elaborazione',
  indexed: 'Indicizzato',
  error: 'Errore',
};

export function detectKind(name: string, mime: string): DocKind | null {
  const ext = name.toLowerCase().split('.').pop() ?? '';
  if (ext === 'pdf' || mime === 'application/pdf') return 'pdf';
  if (['jpg', 'jpeg', 'png'].includes(ext) || ['image/jpeg', 'image/png'].includes(mime)) return 'image';
  if (['md', 'markdown'].includes(ext)) return 'markdown';
  if (ext === 'txt' || mime === 'text/plain') return 'text';
  return null;
}

export const ACCEPT = '.pdf,.md,.markdown,.txt,.jpg,.jpeg,.png';
