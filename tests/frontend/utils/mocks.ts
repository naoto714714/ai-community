import { vi } from 'vitest'
import { Channel, Message } from '@/types/chat'

// モックデータ
export const mockChannels: Channel[] = [
  { id: '1', name: '雑談' },
  { id: '2', name: 'ゲーム' },
  { id: '3', name: '音楽' },
]

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
]

// API モック
export const mockFetch = vi.fn()

export const createMockResponse = (data: any, status = 200) => {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
  }) as Promise<Response>
}

// チャンネル一覧取得のモック
export const mockGetChannels = () => {
  mockFetch.mockResolvedValueOnce(createMockResponse(mockChannels))
}

// メッセージ履歴取得のモック
export const mockGetMessages = (channelId: string, messages = mockMessages) => {
  const filteredMessages = messages.filter(msg => msg.channelId === channelId)
  const response = {
    messages: filteredMessages,
    total: filteredMessages.length,
    hasMore: false,
  }
  mockFetch.mockResolvedValueOnce(createMockResponse(response))
}

// エラーレスポンスのモック
export const mockErrorResponse = (status = 500, message = 'Internal Server Error') => {
  mockFetch.mockRejectedValueOnce(new Error(message))
}

// WebSocketのモック機能
export const WebSocketInstances: MockWebSocket[] = []

export class MockWebSocket {
  public url: string
  public readyState: number = WebSocket.CONNECTING
  public onopen: ((event: Event) => void) | null = null
  public onclose: ((event: CloseEvent) => void) | null = null
  public onmessage: ((event: MessageEvent) => void) | null = null
  public onerror: ((event: Event) => void) | null = null
  public close = vi.fn()
  public send = vi.fn()

  constructor(url: string) {
    this.url = url
    WebSocketInstances.push(this)
    
    // 非同期で接続成功をシミュレート
    setTimeout(() => {
      this.readyState = WebSocket.OPEN
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 0)
  }
}

// リセット関数
export const resetMocks = () => {
  mockFetch.mockClear()
  WebSocketInstances.length = 0
  // グローバルな fetch をモックで置き換え
  global.fetch = mockFetch
}

// バックエンド接続確認のモック
export const setupBackendConnectionMock = () => {
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve({ message: 'AI Community Backend API' }),
  })
}

// チャンネルメッセージ取得のモック
export const mockChannelMessages = (channelId: string, messages: Message[] = []) => {
  const response = {
    messages,
    total: messages.length,
    hasMore: false,
  }
  mockFetch.mockResolvedValueOnce({
    ok: true,
    json: () => Promise.resolve(response),
  })
}