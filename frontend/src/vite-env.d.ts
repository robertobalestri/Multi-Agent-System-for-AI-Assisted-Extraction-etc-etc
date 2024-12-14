/// <reference types="vite/client" />

declare module '../vite-env' {
  interface ImportMetaEnv {
    readonly VITE_API_URL: string;
  }

  interface ImportMeta {
    readonly env: ImportMetaEnv;
  }
}

export type { ImportMetaEnv }; 