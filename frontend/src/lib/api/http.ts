// Client HTTP verso il backend FastAPI. Vedi docs/API_CONTRACT.md.
import type { Doc, DocDetail, EsperApi, SearchHit, TagCount } from '../types';

const BASE: string = import.meta.env.VITE_API_URL ?? '/api';

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(BASE + path, init);
  if (!res.ok) throw new Error((await res.text().catch(() => '')) || res.statusText);
  return res.status === 204 ? (undefined as T) : ((await res.json()) as T);
}

function qs(params: Record<string, string | string[] | undefined>): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (Array.isArray(v)) v.forEach((x) => sp.append(k, x));
    else if (v) sp.set(k, v);
  }
  const s = sp.toString();
  return s ? `?${s}` : '';
}

let inflight = false;

export const httpApi: EsperApi = {
  mode: 'http',
  async listDocuments(params) {
    const docs = await req<Doc[]>(`/documents${qs({ tag: params?.tags })}`);
    inflight = docs.some((d) => d.status === 'queued' || d.status === 'processing');
    return docs;
  },
  getDocument: (id) => req<DocDetail>(`/documents/${id}`),
  async uploadDocuments(files) {
    const body = new FormData();
    files.forEach((f) => body.append('files', f));
    return req<Doc[]>('/documents', { method: 'POST', body });
  },
  updateTags: (id, tags) =>
    req<Doc>(`/documents/${id}/tags`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tags }) }),
  deleteDocument: (id) => req<void>(`/documents/${id}`, { method: 'DELETE' }),
  listTags: () => req<TagCount[]>('/tags'),
  search: (query, params) => req<SearchHit[]>(`/search${qs({ q: query, tag: params?.tags })}`),
  subscribe(cb) {
    // Il backend non spinge eventi: finché ci sono documenti in elaborazione si interroga a intervalli.
    const t = setInterval(() => inflight && cb(), 1500);
    return () => clearInterval(t);
  },
};
