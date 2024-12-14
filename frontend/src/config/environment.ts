import type { ImportMetaEnv } from '../vite-env';

export const config = {
  apiUrl: (import.meta.env as ImportMetaEnv).VITE_API_URL || 'http://localhost:8000/api',
  environment: (import.meta.env as ImportMetaEnv).MODE,
  debug: (import.meta.env as ImportMetaEnv).DEV,
}; 