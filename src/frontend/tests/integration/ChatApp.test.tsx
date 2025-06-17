import { describe, it, expect, vi, beforeEach, afterAll } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '../utils/test-utils';
import { Layout } from '@/components/Layout';
import {
  mockFetch,
  WebSocketInstances,
  resetMocks,
  setupBackendConnectionMock,
  mockChannelMessages,
} from '../utils/mocks';
import { createMockMessage } from '../factories';

describe('ChatApp Integration', () => {
  beforeEach(() => {
    resetMocks();
    setupBackendConnectionMock();
  });

  it('アプリケーションが正常に初期化される', async () => {
    // チャンネルメッセージ取得のモック
    mockChannelMessages();

    render(<Layout />);

    // チャンネル一覧が表示される
    await waitFor(() => {
      expect(screen.getByText('チャンネル')).toBeInTheDocument();
      expect(screen.getAllByText('雑談').length).toBeGreaterThan(0);
      expect(screen.getAllByText('ゲーム').length).toBeGreaterThan(0);
    });

    // メッセージ入力欄が表示される
    expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();

    // WebSocket接続が確立される
    await waitFor(() => {
      expect(WebSocketInstances).toHaveLength(1);
      expect(WebSocketInstances[0].url).toBe('ws://localhost:8000/ws');
    });
  });

  it('チャンネル切り替えでメッセージが更新される', async () => {
    // 初期チャンネル（雑談）のメッセージ
    const chatMessage = createMockMessage({
      id: 'msg-1',
      channelId: '1',
      userId: 'user-1',
      userName: 'ユーザー1',
      content: '雑談メッセージ',
      timestamp: new Date('2025-01-16T10:00:00.000Z'),
      isOwnMessage: false,
    });

    mockChannelMessages([chatMessage], 1, false);

    render(<Layout />);

    // 初期メッセージが表示される
    await waitFor(() => {
      expect(screen.getByText('雑談メッセージ')).toBeInTheDocument();
    });

    // ゲームチャンネルのメッセージモック
    const gameMessage = createMockMessage({
      id: 'msg-2',
      channelId: '2',
      userId: 'user-2',
      userName: 'ユーザー2',
      content: 'ゲームメッセージ',
      timestamp: new Date('2025-01-16T10:05:00.000Z'),
      isOwnMessage: false,
    });

    mockChannelMessages([gameMessage], 1, false);

    // ゲームチャンネルをクリック
    const gameChannels = screen.getAllByText('ゲーム');
    const gameNavLink = gameChannels.find((el) => el.closest('.mantine-NavLink-root'));
    if (gameNavLink) {
      fireEvent.click(gameNavLink);
    }

    // 新しいチャンネルのメッセージが表示される
    await waitFor(() => {
      expect(screen.getByText('ゲームメッセージ')).toBeInTheDocument();
      expect(screen.queryByText('雑談メッセージ')).not.toBeInTheDocument();
    });

    // APIが正しい URL で呼ばれる
    expect(mockFetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/channels/2/messages',
      expect.anything(),
    );
  });

  it('メッセージ送信フローが正常に動作する', async () => {
    // 初期メッセージ取得のモック
    mockChannelMessages();

    render(<Layout />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();
    });

    // WebSocket接続を確立（非同期で接続が確立されるまで待つ）
    await waitFor(() => {
      expect(WebSocketInstances).toHaveLength(1);
    });

    // メッセージを入力して送信
    const input = screen.getByPlaceholderText('メッセージを入力...');
    fireEvent.change(input, { target: { value: 'Test message' } });
    const sendButton = screen
      .getAllByRole('button')
      .find((btn) => btn.querySelector('svg.tabler-icon-send'));
    if (sendButton) {
      fireEvent.click(sendButton);
    }

    // メッセージが即座に表示される（楽観的更新）
    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument();
    });

    // WebSocketでメッセージが送信される
    expect(WebSocketInstances[0].send).toHaveBeenCalledWith(
      expect.stringContaining('Test message'),
    );

    // 入力フィールドがクリアされる
    expect(input).toHaveValue('');
  });

  it('WebSocket経由でメッセージが受信される', async () => {
    // 初期メッセージ取得のモック
    mockChannelMessages();

    render(<Layout />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();
    });

    // WebSocket接続を確立（非同期で接続が確立されるまで待つ）
    await waitFor(() => {
      expect(WebSocketInstances).toHaveLength(1);
    });

    // サーバーからのメッセージ保存成功レスポンスをシミュレート
    const saveResponse = {
      type: 'message:saved',
      data: {
        id: 'msg-test',
        success: true,
      },
    };

    // WebSocketメッセージシミュレーション
    const webSocket = WebSocketInstances[0];
    webSocket.simulateMessage(saveResponse);

    // エラーが発生しないことを確認（コンソールエラーがないこと）
    // 楽観的更新のため、特に UI 変更はない
    expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();
  });

  it('WebSocketエラー時にメッセージがロールバックされる', async () => {
    // 初期メッセージ取得のモック
    mockChannelMessages();

    render(<Layout />);

    await waitFor(() => {
      expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();
    });

    // WebSocket接続を確立（非同期で接続が確立されるまで待つ）
    await waitFor(() => {
      expect(WebSocketInstances).toHaveLength(1);
    });

    // メッセージを送信
    const input = screen.getByPlaceholderText('メッセージを入力...');
    fireEvent.change(input, { target: { value: 'Failed message' } });
    const sendButton = screen
      .getAllByRole('button')
      .find((btn) => btn.querySelector('svg.tabler-icon-send'));
    if (sendButton) {
      fireEvent.click(sendButton);
    }

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

    const webSocket = WebSocketInstances[0];
    if (webSocket.onmessage) {
      // 送信されたメッセージのIDを取得
      const sendCall = webSocket.send.mock.calls[0][0];
      const sentData = JSON.parse(sendCall);
      errorResponse.data.id = sentData.data.id;

      const messageEvent = new MessageEvent('message', {
        data: JSON.stringify(errorResponse),
      });
      webSocket.onmessage(messageEvent);
    }

    // メッセージがロールバックされて削除される
    await waitFor(() => {
      expect(screen.queryByText('Failed message')).not.toBeInTheDocument();
    });
  });

  it('WebSocket未接続時にメッセージ送信が失敗する', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // 初期メッセージ取得のモック
    mockChannelMessages();

    render(<Layout />);

    // WebSocket接続を待ってから未接続状態に設定
    await waitFor(() => {
      expect(WebSocketInstances).toHaveLength(1);
    });

    // WebSocketを未接続状態で開始
    WebSocketInstances[0].readyState = WebSocket.CLOSED;

    await waitFor(() => {
      expect(screen.getByPlaceholderText('メッセージを入力...')).toBeInTheDocument();
    });

    // メッセージを送信しようとする
    const input = screen.getByPlaceholderText('メッセージを入力...');

    await act(async () => {
      fireEvent.change(input, { target: { value: 'Disconnected message' } });
      const sendButton = screen
        .getAllByRole('button')
        .find((btn) => btn.querySelector('svg.tabler-icon-send'));
      if (sendButton) {
        fireEvent.click(sendButton);
      }
    });

    // エラーログが出力されることを確認
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('WebSocket is not connected');
    });

    // WebSocketが閉じている場合、メッセージは楽観的更新で一瞬表示されてからロールバックされる
    // ロールバック処理の完了を待つ
    await waitFor(
      () => {
        expect(screen.queryByText('Disconnected message')).not.toBeInTheDocument();
      },
      { timeout: 3000 },
    );

    // WebSocketのsendは呼ばれない
    expect(WebSocketInstances[0].send).not.toHaveBeenCalled();

    consoleSpy.mockRestore();
  });

  afterAll(() => {
    // グローバルのfetchを元に戻す
    vi.unstubAllGlobals();
  });
});
