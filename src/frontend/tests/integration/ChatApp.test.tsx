import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '../utils/test-utils';
import { Layout } from '@/components/Layout';

// フェッチのモック
const mockFetch = vi.fn();
global.fetch = mockFetch;

// WebSocketのモック
const mockWebSocket = {
  send: vi.fn(),
  close: vi.fn(),
  readyState: WebSocket.OPEN,
  onopen: null as ((event: Event) => void) | null,
  onmessage: null as ((event: MessageEvent) => void) | null,
  onclose: null as ((event: CloseEvent) => void) | null,
  onerror: null as ((event: Event) => void) | null,
};

const MockWebSocketClass = vi.fn().mockImplementation(() => mockWebSocket);
global.WebSocket = MockWebSocketClass as any;

describe('ChatApp Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockClear();

    // バックエンド接続確認のモック
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ message: 'AI Community Backend API' }),
    });
  });

  it('アプリケーションが正常に初期化される', async () => {
    // チャンネルメッセージ取得のモック
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          messages: [],
          total: 0,
          hasMore: false,
        }),
    });

    render(<Layout />);

    // チャンネル一覧が表示される
    await waitFor(() => {
      expect(screen.getByText('チャンネル')).toBeInTheDocument();
      expect(screen.getByText('雑談')).toBeInTheDocument();
      expect(screen.getByText('ゲーム')).toBeInTheDocument();
    });

    // メッセージ入力欄が表示される
    expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();

    // WebSocket接続が確立される
    expect(MockWebSocketClass).toHaveBeenCalledWith('ws://localhost:8000/ws');
  });

  it('チャンネル切り替えでメッセージが更新される', async () => {
    // 初期チャンネル（雑談）のメッセージ
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          messages: [
            {
              id: 'msg-1',
              channelId: '1',
              userId: 'user-1',
              userName: 'ユーザー1',
              content: '雑談メッセージ',
              timestamp: '2025-01-16T10:00:00.000Z',
              isOwnMessage: false,
            },
          ],
          total: 1,
          hasMore: false,
        }),
    });

    render(<Layout />);

    // 初期メッセージが表示される
    await waitFor(() => {
      expect(screen.getByText('雑談メッセージ')).toBeInTheDocument();
    });

    // ゲームチャンネルのメッセージモック
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          messages: [
            {
              id: 'msg-2',
              channelId: '2',
              userId: 'user-2',
              userName: 'ユーザー2',
              content: 'ゲームメッセージ',
              timestamp: '2025-01-16T10:05:00.000Z',
              isOwnMessage: false,
            },
          ],
          total: 1,
          hasMore: false,
        }),
    });

    // ゲームチャンネルをクリック
    fireEvent.click(screen.getByText('ゲーム'));

    // 新しいチャンネルのメッセージが表示される
    await waitFor(() => {
      expect(screen.getByText('ゲームメッセージ')).toBeInTheDocument();
      expect(screen.queryByText('雑談メッセージ')).not.toBeInTheDocument();
    });

    // APIが正しい URL で呼ばれる
    expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/api/channels/2/messages');
  });

  it('メッセージ送信フローが正常に動作する', async () => {
    // 初期メッセージ取得のモック
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          messages: [],
          total: 0,
          hasMore: false,
        }),
    });

    render(<Layout />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();
    });

    // WebSocket接続を確立
    if (mockWebSocket.onopen) {
      mockWebSocket.onopen(new Event('open'));
    }

    // メッセージを入力して送信
    const input = screen.getByPlaceholderText('メッセージを入力...');
    fireEvent.change(input, { target: { value: 'Test message' } });
    fireEvent.click(screen.getByRole('button'));

    // メッセージが即座に表示される（楽観的更新）
    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });

    // WebSocketでメッセージが送信される
    expect(mockWebSocket.send).toHaveBeenCalledWith(expect.stringContaining('Test message'));

    // 入力フィールドがクリアされる
    expect(input).toHaveValue('');
  });

  it('WebSocket経由でメッセージが受信される', async () => {
    // 初期メッセージ取得のモック
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          messages: [],
          total: 0,
          hasMore: false,
        }),
    });

    render(<Layout />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();
    });

    // WebSocket接続を確立
    if (mockWebSocket.onopen) {
      mockWebSocket.onopen(new Event('open'));
    }

    // サーバーからのメッセージ保存成功レスポンスをシミュレート
    const saveResponse = {
      type: 'message:saved',
      data: {
        id: 'msg-test',
        success: true,
      },
    };

    if (mockWebSocket.onmessage) {
      const messageEvent = new MessageEvent('message', {
        data: JSON.stringify(saveResponse),
      });
      mockWebSocket.onmessage(messageEvent);
    }

    // エラーが発生しないことを確認（コンソールエラーがないこと）
    // 楽観的更新のため、特に UI 変更はない
    expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();
  });

  it('WebSocketエラー時にメッセージがロールバックされる', async () => {
    // 初期メッセージ取得のモック
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          messages: [],
          total: 0,
          hasMore: false,
        }),
    });

    render(<Layout />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();
    });

    // WebSocket接続を確立
    if (mockWebSocket.onopen) {
      mockWebSocket.onopen(new Event('open'));
    }

    // メッセージを送信
    const input = screen.getByPlaceholderText('メッセージを入力...');
    fireEvent.change(input, { target: { value: 'Failed message' } });
    fireEvent.click(screen.getByRole('button'));

    // メッセージが表示される（楽観的更新）
    await waitFor(() => {
      expect(screen.getByText('Failed message')).toBeInTheDocument();
    });

    // サーバーからのエラーレスポンスをシミュレート
    const errorResponse = {
      type: 'message:error',
      data: {
        id: expect.any(String),
        success: false,
        error: 'Server error',
      },
    };

    if (mockWebSocket.onmessage) {
      // 送信されたメッセージのIDを取得
      const sendCall = mockWebSocket.send.mock.calls[0][0];
      const sentData = JSON.parse(sendCall);
      errorResponse.data.id = sentData.data.id;

      const messageEvent = new MessageEvent('message', {
        data: JSON.stringify(errorResponse),
      });
      mockWebSocket.onmessage(messageEvent);
    }

    // メッセージがロールバックされて削除される
    await waitFor(() => {
      expect(screen.queryByText('Failed message')).not.toBeInTheDocument();
    });
  });

  it('WebSocket未接続時にメッセージ送信が失敗する', async () => {
    // WebSocketが閉じている状態をシミュレート
    mockWebSocket.readyState = WebSocket.CLOSED;

    // 初期メッセージ取得のモック
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () =>
        Promise.resolve({
          messages: [],
          total: 0,
          hasMore: false,
        }),
    });

    render(<Layout />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();
    });

    // メッセージを送信しようとする
    const input = screen.getByPlaceholderText('メッセージを入力...');
    fireEvent.change(input, { target: { value: 'Disconnected message' } });
    fireEvent.click(screen.getByRole('button'));

    // メッセージが一時的に表示される
    await waitFor(() => {
      expect(screen.getByText('Disconnected message')).toBeInTheDocument();
    });

    // その後、接続エラーによりロールバックされる
    await waitFor(() => {
      expect(screen.queryByText('Disconnected message')).not.toBeInTheDocument();
    });

    // WebSocketのsendは呼ばれない
    expect(mockWebSocket.send).not.toHaveBeenCalled();
  });
});
