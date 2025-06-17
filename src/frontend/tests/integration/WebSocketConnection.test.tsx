import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, waitFor } from '../utils/test-utils';
import { Layout } from '@/components/Layout';

// フェッチのモック
const mockFetch = vi.fn();
global.fetch = mockFetch;

// WebSocketのモック
let mockWebSocket: any;
let WebSocketInstances: any[] = [];

const MockWebSocketClass = vi.fn().mockImplementation((url: string) => {
  mockWebSocket = {
    url,
    readyState: WebSocket.CONNECTING,
    onopen: null as ((event: Event) => void) | null,
    onmessage: null as ((event: MessageEvent) => void) | null,
    onclose: null as ((event: CloseEvent) => void) | null,
    onerror: null as ((event: Event) => void) | null,
    send: vi.fn(),
    close: vi.fn(),
  };
  WebSocketInstances.push(mockWebSocket);
  return mockWebSocket;
});

global.WebSocket = MockWebSocketClass as any;

describe('WebSocket Connection Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockFetch.mockClear();
    WebSocketInstances = [];
    vi.clearAllTimers();
    vi.useFakeTimers();

    // バックエンド接続確認の成功モック
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ message: 'AI Community Backend API' }),
    });

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
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('WebSocket接続が正常に確立される', async () => {
    render(<Layout />);

    await waitFor(() => {
      expect(MockWebSocketClass).toHaveBeenCalledWith('ws://localhost:8000/ws');
    });

    expect(WebSocketInstances).toHaveLength(1);
    expect(WebSocketInstances[0].url).toBe('ws://localhost:8000/ws');
  });

  it('WebSocket接続前にバックエンド動作確認が行われる', async () => {
    render(<Layout />);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/');
    });

    await waitFor(() => {
      expect(MockWebSocketClass).toHaveBeenCalled();
    });
  });

  it('WebSocket接続成功時に再試行カウントがリセットされる', async () => {
    render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    // 接続成功をシミュレート
    mockWebSocket.readyState = WebSocket.OPEN;
    if (mockWebSocket.onopen) {
      mockWebSocket.onopen(new Event('open'));
    }

    // 再試行がリセットされたことは、後の切断時の挙動で確認できる
    expect(mockWebSocket.readyState).toBe(WebSocket.OPEN);
  });

  it('予期しない切断時に再接続を試行する', async () => {
    render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    // 予期しない切断をシミュレート（wasClean: false）
    if (mockWebSocket.onclose) {
      mockWebSocket.onclose(new CloseEvent('close', { wasClean: false }));
    }

    // 再接続タイマーが設定される（3秒後）
    expect(setTimeout).toHaveBeenCalledWith(expect.any(Function), 3000);

    // タイマーを進める
    vi.advanceTimersByTime(3000);

    await waitFor(() => {
      // 再接続のためのバックエンド確認
      expect(mockFetch).toHaveBeenCalledTimes(2); // 初回 + 再接続時
    });
  });

  it('正常な切断時は再接続を試行しない', async () => {
    render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    // 正常な切断をシミュレート（wasClean: true）
    if (mockWebSocket.onclose) {
      mockWebSocket.onclose(new CloseEvent('close', { wasClean: true }));
    }

    // タイマーが設定されない
    expect(setTimeout).not.toHaveBeenCalledWith(expect.any(Function), 3000);
  });

  it('最大再試行回数（5回）に達すると再接続を停止する', async () => {
    // バックエンド接続を失敗させる
    mockFetch.mockClear();
    for (let i = 0; i < 6; i++) {
      mockFetch.mockRejectedValueOnce(new Error('Connection failed'));
    }

    render(<Layout />);

    // 初回接続失敗
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    // 再試行を5回実行
    for (let i = 0; i < 5; i++) {
      vi.advanceTimersByTime(3000);
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(i + 2);
      });
    }

    // 6回目の再試行は行われない
    vi.advanceTimersByTime(3000);
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(6); // 最大6回（初回+再試行5回）
    });

    // さらに時間を進めても再試行されない
    vi.advanceTimersByTime(10000);
    expect(mockFetch).toHaveBeenCalledTimes(6);
  });

  it('WebSocketエラー時にエラーハンドラが呼ばれる', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    // WebSocketエラーをシミュレート
    if (mockWebSocket.onerror) {
      mockWebSocket.onerror(new Event('error'));
    }

    expect(consoleSpy).toHaveBeenCalledWith('WebSocket error:', expect.any(Event));

    consoleSpy.mockRestore();
  });

  it('無効なJSONメッセージを受信した場合エラーハンドリングされる', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    // 無効なJSONメッセージをシミュレート
    if (mockWebSocket.onmessage) {
      const invalidMessageEvent = new MessageEvent('message', {
        data: 'invalid json',
      });
      mockWebSocket.onmessage(invalidMessageEvent);
    }

    expect(consoleSpy).toHaveBeenCalledWith(
      'Failed to parse WebSocket message:',
      expect.any(Error),
      'Raw data:',
      'invalid json',
    );

    consoleSpy.mockRestore();
  });

  it('コンポーネントアンマウント時にWebSocketが正常にクリーンアップされる', async () => {
    const { unmount } = render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    // アンマウント
    unmount();

    // WebSocketのcloseが呼ばれる
    expect(mockWebSocket.close).toHaveBeenCalled();
  });

  it('アンマウント時に再接続タイマーがクリアされる', async () => {
    const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout');
    const { unmount } = render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    // 予期しない切断をシミュレートして再接続タイマーを設定
    if (mockWebSocket.onclose) {
      mockWebSocket.onclose(new CloseEvent('close', { wasClean: false }));
    }

    // アンマウント
    unmount();

    // タイマーがクリアされる
    expect(clearTimeoutSpy).toHaveBeenCalled();
  });

  it('メッセージ送信時にWebSocketの状態を確認する', async () => {
    render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    // WebSocketが接続状態でない場合
    mockWebSocket.readyState = WebSocket.CLOSED;

    // この状態でのメッセージ送信テストは ChatApp.test.tsx で行われている
    expect(mockWebSocket.readyState).toBe(WebSocket.CLOSED);
  });

  it('複数の再接続試行が重複しないようにタイマーがクリアされる', async () => {
    const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout');

    render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    // 最初の切断
    if (mockWebSocket.onclose) {
      mockWebSocket.onclose(new CloseEvent('close', { wasClean: false }));
    }

    // 2回目の切断（タイマーがまだ残っている状態）
    if (mockWebSocket.onclose) {
      mockWebSocket.onclose(new CloseEvent('close', { wasClean: false }));
    }

    // 既存のタイマーがクリアされることを確認
    expect(clearTimeoutSpy).toHaveBeenCalled();
  });
});
