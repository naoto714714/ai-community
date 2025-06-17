import { vi } from 'vitest'

export class MockWebSocket {
  url: string
  readyState: number = 0 // WebSocket.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(url: string) {
    this.url = url
    setTimeout(() => {
      this.readyState = 1 // WebSocket.OPEN
      this.onopen?.(new Event('open'))
    }, 0)
  }

  send = vi.fn((data: string) => {
    // メッセージ送信のモック
  })

  close = vi.fn(() => {
    this.readyState = 3 // WebSocket.CLOSED
    this.onclose?.(new CloseEvent('close'))
  })

  // テスト用ヘルパー
  simulateMessage(data: any) {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }))
  }

  simulateError() {
    this.onerror?.(new Event('error'))
  }

  simulateClose() {
    this.readyState = 3 // WebSocket.CLOSED
    this.onclose?.(new CloseEvent('close'))
  }
}

// グローバルWebSocketのモック
global.WebSocket = MockWebSocket as any