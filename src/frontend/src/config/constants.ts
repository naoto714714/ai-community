// アプリケーション設定定数

// API エンドポイント設定
export const API_CONFIG = {
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  WS_URL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
} as const;

// WebSocket 接続設定
export const WEBSOCKET_CONFIG = {
  MAX_RETRY_COUNT: 5,
  RETRY_DELAY_MS: 3000,
} as const;

// メッセージ設定
export const MESSAGE_CONFIG = {
  MAX_LENGTH: 2000,
  SCROLL_DELAY_MS: 100,
} as const;
