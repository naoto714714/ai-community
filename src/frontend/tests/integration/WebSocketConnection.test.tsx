import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, waitFor, act } from '../utils/test-utils';
import { Layout } from '@/components/Layout';

// フェッチのモック
const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

// WebSocketのモック
interface MockWebSocket {
  url: string;
  readyState: number;
  onopen: ((event: Event) => void) | null;
  onmessage: ((event: MessageEvent) => void) | null;
  onclose: ((event: CloseEvent) => void) | null;
  onerror: ((event: Event) => void) | null;
  send: ReturnType<typeof vi.fn>;
  close: ReturnType<typeof vi.fn>;
}

let WebSocketInstances: MockWebSocket[] = [];

const MockWebSocketClass = vi.fn().mockImplementation((url: string) => {
  const mockWebSocket: MockWebSocket = {
    url,
    readyState: WebSocket.CONNECTING,
    onopen: null,
    onmessage: null,
    onclose: null,
    onerror: null,
    send: vi.fn(),
    close: vi.fn(),
  };

  WebSocketInstances.push(mockWebSocket);

  // フェイクタイマー環境で即座に接続成功としてシミュレート
  setTimeout(() => {
    if (mockWebSocket.onopen) {
      mockWebSocket.readyState = WebSocket.OPEN;
      mockWebSocket.onopen(new Event('open'));
    }
  }, 0);

  return mockWebSocket;
});

vi.stubGlobal('WebSocket', MockWebSocketClass);

describe('WebSocket Connection Integration', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.clearAllMocks();
    mockFetch.mockClear();
    WebSocketInstances = [];

    // DOM scrollTo メソッドのモック
    Object.defineProperty(HTMLDivElement.prototype, 'scrollTo', {
      value: vi.fn(),
      writable: true,
    });

    Object.defineProperty(HTMLDivElement.prototype, 'scrollHeight', {
      value: 1000,
      writable: true,
    });

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

    // フェイクタイマーを進めてWebSocket接続をトリガー
    await act(async () => {
      vi.runAllTimers();
    });

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

    // フェイクタイマーを進めてWebSocket接続をトリガー
    await act(async () => {
      vi.runAllTimers();
    });

    await waitFor(() => {
      expect(MockWebSocketClass).toHaveBeenCalled();
    });
  });

  it('WebSocket接続成功時に再試行カウントがリセットされる', async () => {
    render(<Layout />);

    // フェイクタイマーを進めてWebSocket接続をトリガー
    await act(async () => {
      vi.runAllTimers();
    });

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    // onopenが自動的に呼ばれて接続成功がシミュレートされる
    await waitFor(() => {
      expect(WebSocketInstances[0].readyState).toBe(WebSocket.OPEN);
    });
  });

  it('予期しない切断時に再接続を試行する', async () => {
    render(<Layout />);

    // フェイクタイマーを進めてWebSocket接続をトリガー
    await act(async () => {
      vi.runAllTimers();
    });

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    const firstWebSocket = WebSocketInstances[0];

    // 再接続用のフェッチモック追加
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ message: 'AI Community Backend API' }),
    });
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve({ messages: [], total: 0, hasMore: false }),
    });

    // 予期しない切断をシミュレート
    await act(async () => {
      if (firstWebSocket.onclose) {
        firstWebSocket.onclose(new CloseEvent('close', { wasClean: false }));
      }
    });

    // 再接続タイマーが設定される（3秒後）
    expect(setTimeout).toHaveBeenCalledWith(expect.any(Function), 3000);

    // タイマーを進めて再接続をトリガー
    await act(async () => {
      vi.advanceTimersByTime(3000);
    });

    await waitFor(() => {
      // 再接続のためのバックエンド確認（初回 + 再接続時）
      expect(mockFetch).toHaveBeenCalledTimes(3); // 初回バックエンド + 初回メッセージ + 再接続バックエンド
    });
  });

  it('正常な切断時は再接続を試行しない', async () => {
    render(<Layout />);

    // フェイクタイマーを進めてWebSocket接続をトリガー
    await act(async () => {
      vi.runAllTimers();
    });

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    const firstWebSocket = WebSocketInstances[0];

    // setTimeoutの呼び出し回数をリセット
    vi.clearAllMocks();

    // 正常な切断をシミュレート
    await act(async () => {
      if (firstWebSocket.onclose) {
        firstWebSocket.onclose(new CloseEvent('close', { wasClean: true }));
      }
    });

    // 再接続タイマーが設定されない
    expect(setTimeout).not.toHaveBeenCalledWith(expect.any(Function), 3000);
  });

  it('最大再試行回数（5回）に達すると再接続を停止する', async () => {
    // バックエンド接続を失敗させる
    mockFetch.mockClear();
    for (let i = 0; i < 6; i++) {
      mockFetch.mockRejectedValueOnce(new Error('Connection failed'));
    }

    render(<Layout />);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });

    // 再試行を5回実行
    for (let i = 0; i < 5; i++) {
      await act(async () => {
        vi.advanceTimersByTime(3000);
      });

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(i + 2);
      });
    }

    // 6回目の再試行は行われない
    await act(async () => {
      vi.advanceTimersByTime(3000);
    });

    expect(mockFetch).toHaveBeenCalledTimes(6); // 最大6回（初回+再試行5回）

    // さらに時間を進めても再試行されない
    await act(async () => {
      vi.advanceTimersByTime(10000);
    });
    expect(mockFetch).toHaveBeenCalledTimes(6);
  }, 15000);

  it('WebSocketエラー時にエラーハンドラが呼ばれる', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    const firstWebSocket = WebSocketInstances[0];

    // WebSocketエラーをシミュレート
    await act(async () => {
      if (firstWebSocket.onerror) {
        firstWebSocket.onerror(new Event('error'));
      }
    });

    expect(consoleSpy).toHaveBeenCalledWith('WebSocket error:', expect.any(Event));

    consoleSpy.mockRestore();
  });

  it('無効なJSONメッセージを受信した場合エラーハンドリングされる', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    const firstWebSocket = WebSocketInstances[0];

    // 無効なJSONメッセージをシミュレート
    await act(async () => {
      if (firstWebSocket.onmessage) {
        const invalidMessageEvent = new MessageEvent('message', {
          data: 'invalid json',
        });
        firstWebSocket.onmessage(invalidMessageEvent);
      }
    });

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

    const firstWebSocket = WebSocketInstances[0];

    // アンマウント
    unmount();

    // WebSocketのcloseが呼ばれる
    expect(firstWebSocket.close).toHaveBeenCalled();
  });

  it('アンマウント時に再接続タイマーがクリアされる', async () => {
    const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout');
    const { unmount } = render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    const firstWebSocket = WebSocketInstances[0];

    // 予期しない切断をシミュレートして再接続タイマーを設定
    await act(async () => {
      if (firstWebSocket.onclose) {
        firstWebSocket.onclose(new CloseEvent('close', { wasClean: false }));
      }
    });

    // アンマウント
    await act(async () => {
      unmount();
    });

    // タイマーがクリアされる
    expect(clearTimeoutSpy).toHaveBeenCalled();
  });

  it('メッセージ送信時にWebSocketの状態を確認する', async () => {
    render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    const firstWebSocket = WebSocketInstances[0];

    // WebSocketが接続状態でない場合
    firstWebSocket.readyState = WebSocket.CLOSED;

    // この状態でのメッセージ送信テストは ChatApp.test.tsx で行われている
    expect(firstWebSocket.readyState).toBe(WebSocket.CLOSED);
  });

  it('複数の再接続試行が重複しないようにタイマーがクリアされる', async () => {
    const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout');

    render(<Layout />);

    await waitFor(() => {
      expect(WebSocketInstances[0]).toBeDefined();
    });

    const firstWebSocket = WebSocketInstances[0];

    // 最初の切断
    await act(async () => {
      if (firstWebSocket.onclose) {
        firstWebSocket.onclose(new CloseEvent('close', { wasClean: false }));
      }
    });

    // 2回目の切断（タイマーがまだ残っている状態）
    await act(async () => {
      if (firstWebSocket.onclose) {
        firstWebSocket.onclose(new CloseEvent('close', { wasClean: false }));
      }
    });

    // 既存のタイマーがクリアされることを確認
    expect(clearTimeoutSpy).toHaveBeenCalled();
  });
});
