/**
 * MessageItem コンポーネントテスト
 */
import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MantineProvider } from '@mantine/core';
import { MessageItem } from './MessageItem';
import type { Message } from '../types/chat';

// テスト用のrender関数
function renderWithProvider(component: React.ReactElement) {
  return render(<MantineProvider>{component}</MantineProvider>);
}

describe('MessageItem', () => {
  const utcTimestamp = new Date('2025-01-16T10:00:00.000Z');

  const mockMessage: Message = {
    id: '1',
    channelId: '1',
    userId: 'user1',
    userName: 'Test User',
    userType: 'user',
    content: 'Hello, World!',
    timestamp: utcTimestamp,
    isOwnMessage: false,
  };

  it('メッセージが正しく表示される', () => {
    renderWithProvider(<MessageItem message={mockMessage} />);

    expect(screen.getByText('Hello, World!')).toBeInTheDocument();
    expect(screen.getByText('Test User')).toBeInTheDocument();
  });

  it('自分のメッセージは右寄せで表示される', () => {
    const ownMessage = { ...mockMessage, isOwnMessage: true };
    renderWithProvider(<MessageItem message={ownMessage} />);

    const messageContainer = screen.getByTestId('message-container');
    expect(messageContainer).not.toBeNull();
    expect(messageContainer).toHaveStyle({ justifyContent: 'flex-end' });
  });

  it('空のコンテンツでも正常に表示される', () => {
    const emptyMessage = { ...mockMessage, content: '' };
    renderWithProvider(<MessageItem message={emptyMessage} />);

    expect(screen.getByText('Test User')).toBeInTheDocument();
    // 空のコンテンツでもクラッシュしないことを確認
    expect(screen.getByTestId('message-container')).toBeInTheDocument();
  });

  it('長いメッセージコンテンツが正常に表示される', () => {
    const longContent = 'a'.repeat(1000);
    const longMessage = { ...mockMessage, content: longContent };
    renderWithProvider(<MessageItem message={longMessage} />);

    expect(screen.getByText(longContent)).toBeInTheDocument();
    expect(screen.getByText('Test User')).toBeInTheDocument();
  });

  it('タイムスタンプが正しい形式で表示される', () => {
    renderWithProvider(<MessageItem message={mockMessage} />);

    // HH:mm形式でタイムスタンプが表示されることを確認
    expect(screen.getByText('19:00')).toBeInTheDocument(); // UTCから+9時間（JST）
  });

  it('AIメッセージの場合はAIバッジが表示される', () => {
    const aiMessage = { ...mockMessage, userType: 'ai' as const, userName: 'AI Assistant' };
    renderWithProvider(<MessageItem message={aiMessage} />);

    expect(screen.getByText('AI Assistant')).toBeInTheDocument();
    expect(screen.getByText('AI')).toBeInTheDocument();
  });

  it('ユーザーメッセージの場合はAIバッジが表示されない', () => {
    renderWithProvider(<MessageItem message={mockMessage} />);

    expect(screen.getByText('Test User')).toBeInTheDocument();
    expect(screen.queryByText('AI')).not.toBeInTheDocument();
  });
});
