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
});
