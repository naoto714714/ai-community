/**
 * コンポーネントテスト（最小限・実用版）
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MantineProvider } from '@mantine/core'
import { MessageItem } from '../../../src/frontend/src/components/MessageItem'
import { MessageInput } from '../../../src/frontend/src/components/MessageInput'
import type { Message } from '../../../src/frontend/src/types/chat'
import dayjs from 'dayjs'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'

// dayjsプラグインを設定
dayjs.extend(utc)
dayjs.extend(timezone)

// テスト用のrender関数
function renderWithProvider(component: React.ReactElement) {
  return render(
    <MantineProvider>
      {component}
    </MantineProvider>
  )
}

describe('MessageItem', () => {
  // UTC時間でタイムスタンプを作成
  const utcTimestamp = new Date('2025-01-16T10:00:00.000Z')
  
  const mockMessage: Message = {
    id: '1',
    channelId: '1',
    userId: 'user1',
    userName: 'Test User',
    content: 'Hello, World!',
    timestamp: utcTimestamp,
    isOwnMessage: false
  }

  it('メッセージが正しく表示される', () => {
    renderWithProvider(<MessageItem message={mockMessage} />)

    expect(screen.getByText('Hello, World!')).toBeInTheDocument()
    expect(screen.getByText('Test User')).toBeInTheDocument()
  })

  it('自分のメッセージは右寄せで表示される', () => {
    const ownMessage = { ...mockMessage, isOwnMessage: true }
    renderWithProvider(<MessageItem message={ownMessage} />)

    const messageContainer = screen.getByTestId('message-container')
    expect(messageContainer).not.toBeNull()
    expect(messageContainer).toHaveStyle({ justifyContent: 'flex-end' })
  })
})

describe('MessageInput', () => {
  const mockOnSendMessage = vi.fn()

  beforeEach(() => {
    mockOnSendMessage.mockClear()
  })

  it('テキスト入力が正常に動作する', () => {
    renderWithProvider(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力...')
    fireEvent.change(input, { target: { value: 'テストメッセージ' } })

    expect(input).toHaveValue('テストメッセージ')
  })

  it('Enterキーでメッセージが送信される', () => {
    renderWithProvider(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力...')
    fireEvent.change(input, { target: { value: 'Enterテスト' } })
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false })

    expect(mockOnSendMessage).toHaveBeenCalledWith('Enterテスト')
  })
})