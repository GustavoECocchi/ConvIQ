/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Endereço da API, incluindo o prefixo (`/api`). Padrão: `http://localhost:8000/api`. */
  readonly VITE_API_BASE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
