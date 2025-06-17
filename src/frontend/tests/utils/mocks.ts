import { vi } from 'vitest';
import { Channel, Message } from '@/types/chat';

// モックデータ
export const mockChannels: Channel[] = [
  { id: '1', name: '雑談' },
  { id: '2', name: 'ゲーム' },
  { id: '3', name: '音楽' },
];

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
];

// API モック
export const mockFetch = vi.fn();

export const createMockResponse = (data: unknown, status = 200) => {
  return Promise.resolve({
    ok: status >= 200 && status < 300,
    status,
    json: () => Promise.resolve(data),
  }) as Promise<Response>;
};

// チャンネル一覧取得のモック
export const mockGetChannels = () => {
  mockFetch.mockResolvedValueOnce(createMockResponse(mockChannels));
};

// メッセージ履歴取得のモック
export const mockGetMessages = (channelId: string, messages = mockMessages) => {
  const filteredMessages = messages.filter((msg) => msg.channelId === channelId);
  const response = {
    messages: filteredMessages,
    total: filteredMessages.length,
    hasMore: false,
  };
  mockFetch.mockResolvedValueOnce(createMockResponse(response));
};

// エラーレスポンスのモック
export const mockErrorResponse = (message = 'Internal Server Error') => {
  mockFetch.mockRejectedValueOnce(new Error(message));
};
