import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';
import { MockWebSocket } from './tests/utils/websocket-mock';

// 各テスト後にクリーンアップ
afterEach(() => {
  cleanup();
  // fetchモックのみリセット（他のグローバルモックは維持）
  vi.mocked(global.fetch).mockClear();
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

// WebSocketのグローバルモック（既存の高機能なMockWebSocketクラスを使用）
vi.stubGlobal('WebSocket', MockWebSocket);

// fetchのグローバルモック
vi.stubGlobal('fetch', vi.fn());
