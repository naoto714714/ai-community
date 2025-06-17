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

  // fetch も初期化
  mockFetch.mockClear();
};

// Response オブジェクトを生成するユーティリティ
export const createMockResponse = (
  data: unknown,
  options: {
    status?: number;
    statusText?: string;
    headers?: Record<string, string>;
    ok?: boolean;
  } = {},
) => {
  const {
    status = 200,
    statusText = 'OK',
    headers = { 'Content-Type': 'application/json' },
    ok = status >= 200 && status < 300,
  } = options;

  return {
    ok,
    status,
    statusText,
    headers: new Headers(headers),
    json: () => Promise.resolve(data),
    text: () => Promise.resolve(JSON.stringify(data)),
    arrayBuffer: () => Promise.resolve(new ArrayBuffer(0)),
    blob: () => Promise.resolve(new Blob()),
    formData: () => Promise.resolve(new FormData()),
    clone: vi.fn(),
    body: null,
    bodyUsed: false,
    redirected: false,
    type: 'default' as ResponseType,
    url: '',
  };
};

// バックエンド接続確認のモックをセットアップ
export const setupBackendConnectionMock = () => {
  mockFetch.mockResolvedValueOnce(createMockResponse({ message: 'AI Community Backend API' }));
};

// チャンネルメッセージ取得のモック
export const mockChannelMessages = (messages: unknown[] = [], total = 0, hasMore = false) => {
  mockFetch.mockResolvedValueOnce(
    createMockResponse({
      messages,
      total,
      hasMore,
    }),
  );
};
