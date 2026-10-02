# Esper — frontend

Interfaccia web (Svelte 5 + Vite + TypeScript). Per ora lavora su **dati simulati**: non serve il backend.

```bash
npm install
npm run dev      # http://localhost:5173
npm run check    # type-check con svelte-check
npm run build    # produce dist/
```

- `?q=testo` nell'URL precompila la ricerca.
- Per usare il backend vero: `VITE_API=http npm run dev` (vedi `../docs/API_CONTRACT.md`).

## Struttura

- `src/lib/types.ts` — contratto dati e interfaccia `EsperApi`
- `src/lib/api/` — `mock.ts` (demo), `http.ts` (backend), `seed.ts` (documenti d'esempio)
- `src/lib/store.svelte.ts` — stato globale (runes)
- `src/components/` — componenti UI
