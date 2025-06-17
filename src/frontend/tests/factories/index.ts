import { Channel, Message } from '@/types/chat';

// =============================================================================
// Test Factory Functions
// =============================================================================

// チャンネルファクトリー
export const createMockChannel = (overrides: Partial<Channel> = {}): Channel => ({
  id: 'test-channel-1',
  name: 'テストチャンネル',
  ...overrides,
});

// メッセージファクトリー
export const createMockMessage = (overrides: Partial<Message> = {}): Message => ({
  id: 'test-message-1',
  channelId: 'test-channel-1',
  userId: 'test-user-1',
  userName: 'テストユーザー',
  content: 'テストメッセージ',
  timestamp: new Date('2025-01-16T10:00:00.000Z'),
  isOwnMessage: false,
  ...overrides,
});

// 複数メッセージの生成
export const createMockMessages = (count: number, overrides: Partial<Message> = {}): Message[] => {
  return Array.from({ length: count }, (_, index) =>
    createMockMessage({
      id: `test-message-${index + 1}`,
      content: `テストメッセージ ${index + 1}`,
      timestamp: new Date(`2025-01-16T10:${String(index).padStart(2, '0')}:00.000Z`),
      ...overrides,
    }),
  );
};

// 複数チャンネルの生成
export const createMockChannels = (count: number, overrides: Partial<Channel> = {}): Channel[] => {
  return Array.from({ length: count }, (_, index) =>
    createMockChannel({
      id: `test-channel-${index + 1}`,
      name: `テストチャンネル${index + 1}`,
      ...overrides,
    }),
  );
};

// WebSocketメッセージファクトリー
export const createWebSocketMessage = (overrides: Record<string, unknown> = {}) => ({
  type: 'message',
  channelId: 'test-channel-1',
  message: {
    id: 'test-ws-message-1',
    userId: 'test-user-1',
    userName: 'テストユーザー',
    content: 'WebSocketテストメッセージ',
    timestamp: new Date().toISOString(),
  },
  ...overrides,
});

// APIレスポンスファクトリー
export const createApiResponse = <T>(data: T, overrides: Record<string, unknown> = {}) => ({
  success: true,
  data,
  message: 'Success',
  ...overrides,
});

// エラーレスポンスファクトリー
export const createErrorResponse = (message = 'Test Error', code = 'TEST_ERROR') => ({
  success: false,
  error: {
    message,
    code,
  },
});
