import { vi } from 'vitest';

// WebSocket ready state constants
const WEBSOCKET_READY_STATE = {
  CONNECTING: 0,
  OPEN: 1,
  CLOSING: 2,
  CLOSED: 3,
} as const;

export class MockWebSocket {
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

  simulateClose() {
    this.readyState = WEBSOCKET_READY_STATE.CLOSED;
    this.onclose?.(new CloseEvent('close'));
  }
}

// グローバルWebSocketのモック
global.WebSocket = MockWebSocket as typeof WebSocket;
