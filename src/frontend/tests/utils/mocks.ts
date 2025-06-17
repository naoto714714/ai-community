import { vi } from 'vitest';
import { Channel, Message } from '@/types/chat';

// =============================================================================
// WebSocket Mock
// =============================================================================

// WebSocket ready state constants
const WEBSOCKET_READY_STATE = {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
} as const;

export class MockWebSocket {
  static CONNECTING = WEBSOCKET_READY_STATE.CONNECTING;
  static OPEN = WEBSOCKET_READY_STATE.OPEN;
  static CLOSING = WEBSOCKET_READY_STATE.CLOSING;
  static CLOSED = WEBSOCKET_READY_STATE.CLOSED;

  url: string;
  readyState: number = WEBSOCKET_READY_STATE.CONNECTING;
  onopen: ((event: Event) => void) | null = null;
  onclose: ((event: CloseEvent) => void) | null = null;
  onmessage: ((event: MessageEvent) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;

  constructor(url: string) {
    this.url = url;
    setTimeout(() => {
      this.readyState = WEBSOCKET_READY_STATE.OPEN;
      this.onopen?.(new Event('open'));
    }, 0);
  }

  send = vi.fn(() => {
    // メッセージ送信のモック
  });

  close = vi.fn(() => {
    this.readyState = WEBSOCKET_READY_STATE.CLOSED;
    this.onclose?.(new CloseEvent('close'));
  });

  // テスト用ヘルパー
  simulateMessage(data: unknown) {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }));
  }

  simulateError() {
    this.onerror?.(new Event('error'));
  }

  simulateClose(wasClean = true) {
    this.readyState = WEBSOCKET_READY_STATE.CLOSED;
    this.onclose?.(new CloseEvent('close', { wasClean }));
  }
}

// WebSocketインスタンスの追跡（統合テスト用）
export const WebSocketInstances: MockWebSocket[] = [];

// WebSocketのグローバルモック設定
export const MockWebSocketClass = vi.fn().mockImplementation((url: string) => {
  const instance = new MockWebSocket(url);
  WebSocketInstances.push(instance);
  return instance;
});

// 定数をクラスにコピー
MockWebSocketClass.CONNECTING = WEBSOCKET_READY_STATE.CONNECTING;
MockWebSocketClass.OPEN = WEBSOCKET_READY_STATE.OPEN;
MockWebSocketClass.CLOSING = WEBSOCKET_READY_STATE.CLOSING;
MockWebSocketClass.CLOSED = WEBSOCKET_READY_STATE.CLOSED;

vi.stubGlobal('WebSocket', MockWebSocketClass);

// =============================================================================
// Fetch Mock
// =============================================================================

export const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

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

// =============================================================================
// Mock Data
// =============================================================================

export const mockChannels: Channel[] = [
  { id: '1', name: '雑談' },
  { id: '2', name: 'ゲーム' },
  { id: '3', name: '音楽' },
];

export const mockMessages: Message[] = [
  {
    id: 'msg-1',
    channelId: '1',
    userId: 'user-1',
    userName: 'テストユーザー1',
    content: 'こんにちは！',
    timestamp: new Date('2025-01-16T10:00:00.000Z'),
    isOwnMessage: false,
  },
  {
    id: 'msg-2',
    channelId: '1',
    userId: 'user-2',
    userName: 'テストユーザー2',
    content: 'お疲れ様です',
    timestamp: new Date('2025-01-16T10:01:00.000Z'),
    isOwnMessage: true,
  },
];

// =============================================================================
// Helper Functions
// =============================================================================

// モック状態のリセット
export const resetMocks = () => {
  mockFetch.mockReset();
  WebSocketInstances.length = 0;
};

// バックエンド接続確認のモックをセットアップ
export const setupBackendConnectionMock = () => {
  mockFetch.mockResolvedValueOnce(createMockResponse({ message: 'AI Community Backend API' }));
};

// チャンネル一覧取得のモック
export const mockGetChannels = () => {
  mockFetch.mockResolvedValueOnce(createMockResponse(mockChannels));
};

// メッセージ履歴取得のモック
export const mockGetMessages = (channelId: string, messages = mockMessages) => {
  const filteredMessages = messages.filter((msg) => msg.channelId === channelId);
  const response = {
    messages: filteredMessages,
    total: filteredMessages.length,
    hasMore: false,
  };
  mockFetch.mockResolvedValueOnce(createMockResponse(response));
};

// チャンネルメッセージ取得のモック（レガシー互換）
export const mockChannelMessages = (messages: unknown[] = [], total = 0, hasMore = false) => {
  mockFetch.mockResolvedValueOnce(
    createMockResponse({
      messages,
      total,
      hasMore,
    }),
  );
};

// エラーレスポンスのモック
export const mockErrorResponse = (message = 'Internal Server Error') => {
  mockFetch.mockRejectedValueOnce(new Error(message));
};
