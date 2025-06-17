import { vi } from 'vitest';

// DOM scrollTo メソッドのモック
Object.defineProperty(HTMLDivElement.prototype, 'scrollTo', {
  value: vi.fn(),
  writable: true,
});

Object.defineProperty(HTMLDivElement.prototype, 'scrollHeight', {
  value: 1000,
  writable: true,
});

// フェッチのモック
export const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// WebSocketのモック
export const MockWebSocketClass = vi.fn();
MockWebSocketClass.OPEN = 1;
MockWebSocketClass.CLOSED = 3;

export const mockWebSocket = {
  send: vi.fn(),
  close: vi.fn(),
  readyState: MockWebSocketClass.OPEN,
  onopen: null as ((event: Event) => void) | null,
  onmessage: null as ((event: MessageEvent) => void) | null,
  onclose: null as ((event: CloseEvent) => void) | null,
  onerror: null as ((event: Event) => void) | null,
};

MockWebSocketClass.mockImplementation(() => mockWebSocket);
vi.stubGlobal('WebSocket', MockWebSocketClass);

// WebSocketの状態をリセット
export const resetWebSocketState = () => {
  mockWebSocket.readyState = MockWebSocketClass.OPEN;
  mockWebSocket.send.mockClear();
  mockWebSocket.close.mockClear();
  mockWebSocket.onopen = null;
  mockWebSocket.onmessage = null;
  mockWebSocket.onclose = null;
  mockWebSocket.onerror = null;
};

// バックエンド接続確認のモックをセットアップ
export const setupBackendConnectionMock = () => {
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve({ message: 'AI Community Backend API' }),
  });
};

// チャンネルメッセージ取得のモック
export const mockChannelMessages = (messages: unknown[] = [], total = 0, hasMore = false) => {
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: () =>
      Promise.resolve({
        messages,
        total,
        hasMore,
      }),
  });
};
