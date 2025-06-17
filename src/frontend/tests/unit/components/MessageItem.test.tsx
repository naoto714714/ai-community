import { describe, it, expect } from 'vitest';
import { render, screen } from '../../utils/test-utils';
import { MessageItem } from '@/components/MessageItem';
import type { Message } from '@/types/chat';
import dayjs from 'dayjs';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';

// dayjsプラグインを設定
dayjs.extend(utc);
dayjs.extend(timezone);

describe('MessageItem', () => {
  // UTC時間でタイムスタンプを作成し、コンポーネントと同じ方法でローカル時間での期待値を計算
  const utcTimestamp = new Date('2025-01-16T10:00:00.000Z');
  const expectedTimeString = dayjs(utcTimestamp).format('HH:mm');

  const mockMessage: Message = {
    id: '1',
    channelId: '1',
    userId: 'user1',
    userName: 'Test User',
    content: 'Hello, World!',
    timestamp: utcTimestamp,
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

    const messageContainer = screen.getByTestId('message-container');
    expect(messageContainer).not.toBeNull();
    expect(messageContainer).toHaveStyle({ justifyContent: 'flex-end' });
  });

  it('他人のメッセージは左寄せで表示される', () => {
    render(<MessageItem message={mockMessage} />);

    const messageContainer = screen.getByTestId('message-container');
    expect(messageContainer).not.toBeNull();
    expect(messageContainer).toHaveStyle({ justifyContent: 'flex-start' });
  });

  it('タイムスタンプが正しくフォーマットされる', () => {
    render(<MessageItem message={mockMessage} />);

    // UTC時間でフォーマットした期待値を使用してテスト
    expect(screen.getByText(expectedTimeString)).toBeInTheDocument();
  });

  it('自分のメッセージと他人のメッセージで色が異なる', () => {
    // 他人のメッセージ
    const { rerender } = render(<MessageItem message={mockMessage} />);

    const otherMessageBubble = screen.getByTestId('message-bubble');
    expect(otherMessageBubble).not.toBeNull();
    expect(otherMessageBubble).toHaveStyle({ backgroundColor: 'var(--mantine-color-gray-7)' });

    // 自分のメッセージ
    const ownMessage = { ...mockMessage, isOwnMessage: true };
    rerender(<MessageItem message={ownMessage} />);

    const ownMessageBubble = screen.getByTestId('message-bubble');
    expect(ownMessageBubble).not.toBeNull();
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
