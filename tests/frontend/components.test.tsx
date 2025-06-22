/**
 * コンポーネントテスト（最小限・実用版）
 */
import React from 'react'
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MantineProvider } from '@mantine/core'
import { MessageItem } from '../../../src/frontend/src/components/MessageItem'
import { MessageInput } from '../../../src/frontend/src/components/MessageInput'
import type { Message } from '../../../src/frontend/src/types/chat'

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
  let originalPlatform: string

  beforeEach(() => {
    mockOnSendMessage.mockClear()
    originalPlatform = navigator.platform
  })

  afterEach(() => {
    Object.defineProperty(navigator, 'platform', {
      value: originalPlatform,
      writable: true
    })
  })

  it('テキスト入力が正常に動作する（Mac）', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'MacIntel',
      writable: true
    })
    
    renderWithProvider(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力... (⌘+Enterで送信)')
    fireEvent.change(input, { target: { value: 'テストメッセージ' } })

    expect(input).toHaveValue('テストメッセージ')
  })

  it('テキスト入力が正常に動作する（Windows）', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'Win32',
      writable: true
    })
    
    renderWithProvider(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力... (Ctrl+Enterで送信)')
    fireEvent.change(input, { target: { value: 'テストメッセージ' } })

    expect(input).toHaveValue('テストメッセージ')
  })

  it('Command+Enterキーでメッセージが送信される（Mac）', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'MacIntel',
      writable: true
    })
    
    renderWithProvider(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力... (⌘+Enterで送信)')
    fireEvent.change(input, { target: { value: 'Command+Enterテスト' } })
    fireEvent.keyDown(input, { key: 'Enter', metaKey: true })

    expect(mockOnSendMessage).toHaveBeenCalledTimes(1)
    expect(mockOnSendMessage).toHaveBeenCalledWith('Command+Enterテスト')
  })

  it('Ctrl+Enterキーでメッセージが送信される（Windows）', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'Win32',
      writable: true
    })
    
    renderWithProvider(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力... (Ctrl+Enterで送信)')
    fireEvent.change(input, { target: { value: 'Ctrl+Enterテスト' } })
    fireEvent.keyDown(input, { key: 'Enter', ctrlKey: true })

    expect(mockOnSendMessage).toHaveBeenCalledTimes(1)
    expect(mockOnSendMessage).toHaveBeenCalledWith('Ctrl+Enterテスト')
  })

  it('Shift+Enterキーではメッセージが送信されない（Mac）', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'MacIntel',
      writable: true
    })
    
    renderWithProvider(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力... (⌘+Enterで送信)')
    fireEvent.change(input, { target: { value: 'Shift+Enterテスト' } })
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: true })

    expect(mockOnSendMessage).toHaveBeenCalledTimes(0)
  })

  it('単純なEnterキーではメッセージが送信されない（Mac）', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'MacIntel',
      writable: true
    })
    
    renderWithProvider(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力... (⌘+Enterで送信)')
    fireEvent.change(input, { target: { value: '単純なEnterテスト' } })
    fireEvent.keyDown(input, { key: 'Enter' })

    expect(mockOnSendMessage).toHaveBeenCalledTimes(0)
  })

  it('MacでCtrl+Enterを押しても送信されない', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'MacIntel',
      writable: true
    })
    
    renderWithProvider(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力... (⌘+Enterで送信)')
    fireEvent.change(input, { target: { value: 'MacでCtrl+Enterテスト' } })
    fireEvent.keyDown(input, { key: 'Enter', ctrlKey: true })

    expect(mockOnSendMessage).toHaveBeenCalledTimes(0)
  })

  it('WindowsでCommand+Enterを押しても送信されない', () => {
    Object.defineProperty(navigator, 'platform', {
      value: 'Win32',
      writable: true
    })
    
    renderWithProvider(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力... (Ctrl+Enterで送信)')
    fireEvent.change(input, { target: { value: 'WindowsでCommand+Enterテスト' } })
    fireEvent.keyDown(input, { key: 'Enter', metaKey: true })

    expect(mockOnSendMessage).toHaveBeenCalledTimes(0)
  })
})
