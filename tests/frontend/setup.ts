import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

// 各テスト後にクリーンアップ
afterEach(() => {
  cleanup()
})

// グローバルモック設定
vi.mock('nanoid', () => ({
  nanoid: () => 'test-id-12345'
}))

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
}))

vi.stubGlobal('WebSocket', MockWebSocket)

// fetchのグローバルモック
global.fetch = vi.fn()