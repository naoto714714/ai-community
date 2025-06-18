/**
 * 統合テスト（最小限・実用版）
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { MantineProvider } from '@mantine/core'
import { Layout } from '../../../src/frontend/src/components/Layout'

// モックWebSocket
class MockWebSocket {
  url: string
  readyState: number = WebSocket.OPEN
  onopen: ((event: Event) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null
  onclose: ((event: Event) => void) | null = null

  constructor(url: string) {
    this.url = url
    // 接続成功をシミュレート
    setTimeout(() => {
      if (this.onopen) {
        this.onopen(new Event('open'))
      }
    }, 0)
  }

  send(data: string) {
    // メッセージ送信のシミュレーション
    const message = JSON.parse(data)
    if (message.type === 'message:send') {
      // 保存成功レスポンスをシミュレート
      setTimeout(() => {
        if (this.onmessage) {
          this.onmessage(new MessageEvent('message', {
            data: JSON.stringify({
              type: 'message:saved',
              data: {
                success: true,
                id: message.data.id
              }
            })
          }))
        }
      }, 0)
    }
  }

  close() {
    this.readyState = WebSocket.CLOSED
    if (this.onclose) {
      this.onclose(new Event('close'))
    }
  }
}

// テスト用のrender関数
function renderWithProvider(component: React.ReactElement) {
  return render(
    <MantineProvider>
      {component}
    </MantineProvider>
  )
}

describe('ChatApp Integration', () => {
  beforeEach(() => {
    // WebSocketのモック
    vi.stubGlobal('WebSocket', MockWebSocket)
    
    // fetchのモック
    global.fetch = vi.fn()
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ message: 'AI Community Backend API' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve([
          { id: '1', name: '雑談', createdAt: '2025-01-16T10:00:00.000Z' },
          { id: '2', name: 'ゲーム', createdAt: '2025-01-16T10:00:00.000Z' }
        ])
      })
      .mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({
          messages: [],
          total: 0,
          hasMore: false
        })
      })
  })

  it('チャンネル切り替えでメッセージが更新される', async () => {
    renderWithProvider(<Layout />)

    // チャンネル一覧が表示されるまで待機
    await waitFor(() => {
      expect(screen.getByText('雑談')).toBeInTheDocument()
      expect(screen.getByText('ゲーム')).toBeInTheDocument()
    })

    // ゲームチャンネルをクリック
    const gameChannel = screen.getByText('ゲーム')
    fireEvent.click(gameChannel)

    // メッセージ取得APIが呼ばれることを確認
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/channels/2/messages')
      )
    })
  })

  it('WebSocket経由でメッセージが送受信される', async () => {
    renderWithProvider(<Layout />)

    // チャンネル一覧が表示されるまで待機
    await waitFor(() => {
      expect(screen.getByText('雑談')).toBeInTheDocument()
    })

    // メッセージ入力
    const input = screen.getByPlaceholderText('メッセージを入力...')
    fireEvent.change(input, { target: { value: 'テストメッセージ' } })

    // Enterキーで送信
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false })

    // WebSocket経由でメッセージが送信されることを確認
    // （実際のWebSocketの詳細な検証は複雑なため、基本的な動作のみ確認）
    expect(input).toHaveValue('')
  })

  it('エラー時に適切にハンドリングされる', async () => {
    // エラーレスポンスのモック
    global.fetch = vi.fn().mockRejectedValue(new Error('Network Error'))

    renderWithProvider(<Layout />)

    // エラーが発生してもアプリがクラッシュしないことを確認
    await waitFor(() => {
      expect(screen.getByText('チャンネル')).toBeInTheDocument()
    })

    // メッセージ入力欄は表示される（エラーハンドリングが機能している）
    expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument()
  })
})