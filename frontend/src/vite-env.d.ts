/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** 未設定時前端改用同源 `/ws/gps`。 */
  readonly VITE_WS_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
