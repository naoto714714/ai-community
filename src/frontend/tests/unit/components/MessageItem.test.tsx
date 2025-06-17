import { describe, it, expect } from 'vitest';
import { render, screen } from '../../utils/test-utils';
import { MessageItem } from '@/components/MessageItem';
import type { Message } from '@/types/chat';

describe('MessageItem', () => {
  const mockMessage: Message = {
    id: '1',
    channelId: '1',
    userId: 'user1',
    userName: 'Test User',
    content: 'Hello, World!',
    timestamp: new Date('2025-01-16T10:00:00.000Z'),
    isOwnMessage: false,
  };

  it('メッセージを正しく表示する', () => {
    render(<MessageItem message={mockMessage} />);

    expect(screen.getByText('Hello, World!')).toBeInTheDocument();
    expect(screen.getByText('Test User')).toBeInTheDocument();
  });

  it('自分のメッセージは右寄せで表示される', () => {
    const ownMessage = { ...mockMessage, isOwnMessage: true };
    render(<MessageItem message={ownMessage} />);

    const messageContainer = screen.getByText('Hello, World!').closest('div')
      ?.parentElement?.parentElement;
    expect(messageContainer).toHaveStyle({ justifyContent: 'flex-end' });
  });

  it('他人のメッセージは左寄せで表示される', () => {
    render(<MessageItem message={mockMessage} />);

    const messageContainer = screen.getByText('Hello, World!').closest('div')
      ?.parentElement?.parentElement;
    expect(messageContainer).toHaveStyle({ justifyContent: 'flex-start' });
  });

  it('タイムスタンプが正しくフォーマットされる', () => {
    render(<MessageItem message={mockMessage} />);

    // dayjs形式で表示されることを確認（HH:mm形式）
    expect(screen.getByText('10:00')).toBeInTheDocument();
  });

  it('自分のメッセージと他人のメッセージで色が異なる', () => {
    // 他人のメッセージ
    const { rerender } = render(<MessageItem message={mockMessage} />);

    const otherMessageBubble = screen.getByText('Hello, World!').parentElement;
    expect(otherMessageBubble).toHaveStyle({ backgroundColor: 'var(--mantine-color-gray-7)' });

    // 自分のメッセージ
    const ownMessage = { ...mockMessage, isOwnMessage: true };
    rerender(<MessageItem message={ownMessage} />);

    const ownMessageBubble = screen.getByText('Hello, World!').parentElement;
    expect(ownMessageBubble).toHaveStyle({ backgroundColor: 'var(--mantine-color-blue-6)' });
  });

  it('長いメッセージが正しく折り返される', () => {
    const longMessage = {
      ...mockMessage,
      content: 'これは非常に長いメッセージです。'.repeat(20),
    };
    render(<MessageItem message={longMessage} />);

    const messageText = screen.getByText(longMessage.content);
    expect(messageText).toHaveStyle({ wordBreak: 'break-word' });
  });
});
