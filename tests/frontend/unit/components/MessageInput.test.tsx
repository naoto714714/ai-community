import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '../../utils/test-utils'
import { MessageInput } from '@/components/MessageInput'

describe('MessageInput', () => {
  const mockOnSendMessage = vi.fn()

  beforeEach(() => {
    mockOnSendMessage.mockClear()
  })

  it('プレースホルダーが正しく表示される', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />)

    expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument()
  })

  it('テキスト入力が正常に動作する', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力...')
    fireEvent.change(input, { target: { value: 'テストメッセージ' } })

    expect(input).toHaveValue('テストメッセージ')
  })

  it('送信ボタンクリックでメッセージが送信される', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力...')
    const sendButton = screen.getByRole('button')

    fireEvent.change(input, { target: { value: 'テストメッセージ' } })
    fireEvent.click(sendButton)

    expect(mockOnSendMessage).toHaveBeenCalledWith('テストメッセージ')
  })

  it('Enterキーでメッセージが送信される', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力...')
    fireEvent.change(input, { target: { value: 'Enterテスト' } })
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false })

    expect(mockOnSendMessage).toHaveBeenCalledWith('Enterテスト')
  })

  it('Shift+Enterでは送信されない', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力...')
    fireEvent.change(input, { target: { value: 'Shift+Enterテスト' } })
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: true })

    expect(mockOnSendMessage).not.toHaveBeenCalled()
  })

  it('空文字では送信されない', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力...')
    const sendButton = screen.getByRole('button')

    fireEvent.change(input, { target: { value: '   ' } }) // 空白のみ
    fireEvent.click(sendButton)

    expect(mockOnSendMessage).not.toHaveBeenCalled()
  })

  it('送信後に入力フィールドがクリアされる', async () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力...')
    const sendButton = screen.getByRole('button')

    fireEvent.change(input, { target: { value: 'クリアテスト' } })
    fireEvent.click(sendButton)

    await waitFor(() => {
      expect(input).toHaveValue('')
    })
  })

  it('空文字の時は送信ボタンが無効化される', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />)

    const sendButton = screen.getByRole('button')

    // 初期状態では無効化されている
    expect(sendButton).toBeDisabled()

    // テキスト入力後は有効化される
    const input = screen.getByPlaceholderText('メッセージを入力...')
    fireEvent.change(input, { target: { value: 'テスト' } })
    expect(sendButton).toBeEnabled()

    // 空にすると再度無効化される
    fireEvent.change(input, { target: { value: '' } })
    expect(sendButton).toBeDisabled()
  })

  it('最大文字数制限が適用される', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力...')
    expect(input).toHaveAttribute('maxlength', '2000')
  })

  it('IME入力中はEnterキーで送信されない', () => {
    render(<MessageInput onSendMessage={mockOnSendMessage} />)

    const input = screen.getByPlaceholderText('メッセージを入力...')
    
    // IME入力開始
    fireEvent.compositionStart(input)
    fireEvent.change(input, { target: { value: 'IMEテスト' } })
    
    // IME入力中のEnterキー
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false })
    
    expect(mockOnSendMessage).not.toHaveBeenCalled()
    
    // IME入力終了後のEnterキー
    fireEvent.compositionEnd(input)
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false })
    
    expect(mockOnSendMessage).toHaveBeenCalledWith('IMEテスト')
  })
})