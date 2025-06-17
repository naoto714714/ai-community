import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// 各テスト後にクリーンアップ
afterEach(() => {
  cleanup();
});

// matchMediaのモック
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // Deprecated
    removeListener: vi.fn(), // Deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// ResizeObserverのモック
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// グローバルモック設定
vi.mock('nanoid', () => ({
  nanoid: () => 'test-id-12345',
}));

// WebSocketのグローバルモック
const MockWebSocket = vi.fn().mockImplementation((url: string) => ({
  url,
  readyState: WebSocket.CONNECTING,
  onopen: null,
  onclose: null,
  onmessage: null,
  onerror: null,
  send: vi.fn(),
  close: vi.fn(),
}));

vi.stubGlobal('WebSocket', MockWebSocket);

// fetchのグローバルモック
global.fetch = vi.fn();
