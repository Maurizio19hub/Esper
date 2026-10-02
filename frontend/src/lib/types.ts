// Contratto dati tra interfaccia e backend (vedi docs/API_CONTRACT.md).

export type DocKind = 'pdf' | 'image' | 'markdown' | 'text';
export type DocStatus = 'queued' | 'processing' | 'indexed' | 'error';
export type ChunkSource = 'text' | 'ocr' | 'visual';
export type MatchVia = 'semantic' | 'keyword' | 'both';

export interface Doc {
  id: number;
  name: string;
  kind: DocKind;
  mime: string;
  size: number;
  status: DocStatus;
  /** 0..1, significativo solo mentre lo stato è `processing`. */
  progress: number;
  error?: string;
  tags: string[];
  createdAt: string;
  pages?: number;
  chunkCount: number;
  excerpt: string;
  thumbnailUrl?: string;
  fileUrl?: string;
}

export interface Chunk {
  id: number;
  index: number;
  page?: number;
  text: string;
  source: ChunkSource;
}

export interface DocDetail extends Doc {
  chunks: Chunk[];
}

export interface SearchMatch {
  chunkId: number;
  page?: number;
  text: string;
  score: number;
  source: ChunkSource;
  via: MatchVia;
}

export interface SearchHit {
  doc: Doc;
  score: number;
  matches: SearchMatch[];
}

export interface TagCount {
  name: string;
  count: number;
}

export interface EsperApi {
  mode: 'mock' | 'http';
  listDocuments(params?: { tags?: string[] }): Promise<Doc[]>;
  getDocument(id: number): Promise<DocDetail>;
  uploadDocuments(files: File[]): Promise<Doc[]>;
  updateTags(id: number, tags: string[]): Promise<Doc>;
  deleteDocument(id: number): Promise<void>;
  listTags(): Promise<TagCount[]>;
  search(query: string, params?: { tags?: string[] }): Promise<SearchHit[]>;
  /** Notifica quando qualcosa cambia lato server (stato di elaborazione, ecc.). */
  subscribe(cb: () => void): () => void;
}
