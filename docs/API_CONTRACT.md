# Contratto API Esper (frontend ⇄ backend)

La UI (`frontend/`) usa l'interfaccia `EsperApi` definita in `frontend/src/lib/types.ts`.
In modalità demo è implementata da `lib/api/mock.ts` (dati simulati); con `VITE_API=http`
usa `lib/api/http.ts`, che chiama il backend FastAPI qui descritto (base `/api`, o `VITE_API_URL`).
In sviluppo Vite inoltra `/api/*` a `http://127.0.0.1:8000/*`.

Tutti i JSON usano chiavi **camelCase**.

| Metodo | Percorso | Descrizione |
|---|---|---|
| `GET` | `/documents?tag=a&tag=b` | Elenca i documenti (filtro AND sulle etichette) → `Doc[]` |
| `POST` | `/documents` | Carica file, `multipart/form-data` con campo `files` ripetuto → `Doc[]` (stato `queued`) |
| `GET` | `/documents/{id}` | Dettaglio con i frammenti → `DocDetail` |
| `PATCH` | `/documents/{id}/tags` | Corpo `{ "tags": string[] }` → `Doc` aggiornato |
| `DELETE` | `/documents/{id}` | Elimina file, frammenti e vettori → `204` |
| `GET` | `/documents/{id}/file` | File originale (anteprima e download) |
| `GET` | `/tags` | `TagCount[]`, ordinati per conteggio |
| `GET` | `/search?q=...&tag=a` | Ricerca ibrida → `SearchHit[]`, ordinati per `score` decrescente |

## Tipi principali

```ts
Doc {
  id, name, kind: 'pdf'|'image'|'markdown'|'text', mime, size,
  status: 'queued'|'processing'|'indexed'|'error', progress (0..1), error?,
  tags: string[], createdAt (ISO 8601), pages?, chunkCount, excerpt,
  thumbnailUrl?, fileUrl?            // es. "/api/documents/12/file"
}
Chunk       { id, index, page?, text, source: 'text'|'ocr'|'visual' }
DocDetail   = Doc + { chunks: Chunk[] }
SearchMatch { chunkId, page?, text, score, source, via: 'semantic'|'keyword'|'both' }
SearchHit   { doc: Doc, score (0..1), matches: SearchMatch[] }   // al massimo ~3 match per documento
TagCount    { name, count }
```

## Note di comportamento

- L'upload risponde subito; l'elaborazione (estrazione, chunking, embedding) è asincrona.
  La UI interroga `GET /documents` ogni 1,5 s finché c'è almeno un documento `queued`/`processing`.
- Le etichette sono normalizzate lato client (minuscolo, trattini al posto degli spazi); il backend dovrebbe fare lo stesso.
- `via` indica quale ramo della ricerca ha prodotto il frammento (vettoriale, full-text o entrambi).
- Gli errori sono risposte HTTP non-2xx con un messaggio testuale, mostrato nelle notifiche.
