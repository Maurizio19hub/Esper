import type { EsperApi } from '../types';
import { httpApi } from './http';
import { mockApi } from './mock';

/** `VITE_API=http` usa il backend vero, altrimenti dati simulati. */
export const api: EsperApi = import.meta.env.VITE_API === 'http' ? httpApi : mockApi;
