import { describe, it, expect, vi, beforeAll, afterAll } from 'vitest';
import { render, screen, waitFor } from '../../utils/test-utils';
import { MessageList } from '@/components/MessageList';
import type { Message } from '@/types/chat';

// scrollToのモック
const mockScrollTo = vi.fn();
let originalScrollTo: typeof HTMLElement.prototype.scrollTo;

describe('MessageList', () => {
  beforeAll(() => {
    // scrollToのスタブを設定
    originalScrollTo = HTMLElement.prototype.scrollTo;
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
      value: mockScrollTo,
      writable: true,
    });
  });

  afterAll(() => {
    // scrollToのスタブを復元
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
      value: originalScrollTo,
      writable: true,
    });
  });

  const mockMessages: Message[] = [
    {
      id: 'msg-1',
      channelId: '1',
      userId: 'user-1',
      userName: 'ユーザー1',
      content: 'こんにちは！',
      timestamp: new Date('2025-01-16T10:00:00.000Z'),
      isOwnMessage: false,
    },
    {
      id: 'msg-2',
      channelId: '1',
      userId: 'user-2',
      userName: 'ユーザー2',
      content: 'お疲れ様です',
      timestamp: new Date('2025-01-16T10:01:00.000Z'),
      isOwnMessage: true,
    },
  ];

  beforeEach(() => {
    mockScrollTo.mockClear();
    vi.clearAllTimers();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('メッセージ一覧が正しく表示される', () => {
    render(<MessageList messages={mockMessages} />);

    expect(screen.getByText('こんにちは！')).toBeInTheDocument();
    expect(screen.getByText('お疲れ様です')).toBeInTheDocument();
    expect(screen.getByText('ユーザー1')).toBeInTheDocument();
    expect(screen.getByText('ユーザー2')).toBeInTheDocument();
  });

  it('メッセージがない場合は案内メッセージが表示される', () => {
    render(<MessageList messages={[]} />);

    expect(screen.getByText('まだメッセージがありません')).toBeInTheDocument();
    expect(screen.queryByText('こんにちは！')).not.toBeInTheDocument();
  });

  it('各メッセージが正しい順序で表示される', () => {
    render(<MessageList messages={mockMessages} />);

    const messageElements = screen.getAllByText(/こんにちは！|お疲れ様です/);
    expect(messageElements).toHaveLength(2);

    // 配列の順序通りに表示される
    expect(messageElements[0]).toHaveTextContent('こんにちは！');
    expect(messageElements[1]).toHaveTextContent('お疲れ様です');
  });

  it('メッセージ追加時にスクロールが実行される', async () => {
    const { rerender } = render(<MessageList messages={[mockMessages[0]]} />);

    // 最初のレンダリング後のスクロール
    await waitFor(() => {
      vi.runAllTimers();
    });

    // メッセージを追加
    rerender(<MessageList messages={mockMessages} />);

    // タイマーを進めてスクロールが呼ばれることを確認
    await waitFor(() => {
      vi.runAllTimers();
      expect(mockScrollTo).toHaveBeenCalled();
    });
  });

  it('スクロール動作が正しく設定される', async () => {
    render(<MessageList messages={mockMessages} />);

    await waitFor(() => {
      vi.runAllTimers();
    });

    expect(mockScrollTo).toHaveBeenCalledWith({
      top: expect.any(Number),
      behavior: 'smooth',
    });
  });

  it('メッセージの更新時に既存のタイマーがクリアされる', async () => {
    const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout');
    const { rerender } = render(<MessageList messages={[mockMessages[0]]} />);

    // 最初のレンダリング
    await waitFor(() => {
      vi.runAllTimers();
    });

    // メッセージを更新
    rerender(<MessageList messages={mockMessages} />);

    // clearTimeoutが呼ばれることを確認
    expect(clearTimeoutSpy).toHaveBeenCalled();
  });

  it('コンポーネントアンマウント時にタイマーがクリアされる', () => {
    const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout');
    const { unmount } = render(<MessageList messages={mockMessages} />);

    unmount();

    expect(clearTimeoutSpy).toHaveBeenCalled();
  });

  it('ScrollAreaが正しく設定される', () => {
    render(<MessageList messages={mockMessages} />);

    // ScrollAreaコンポーネントが高さ100%で設定されている
    const scrollArea = document.querySelector('[data-mantine-component="ScrollArea"]');
    expect(scrollArea).toBeInTheDocument();
  });

  it('大量のメッセージも正しく表示される', () => {
    const manyMessages: Message[] = Array.from({ length: 50 }, (_, i) => ({
      id: `msg-${i}`,
      channelId: '1',
      userId: `user-${i % 3}`,
      userName: `ユーザー${i % 3}`,
      content: `メッセージ ${i + 1}`,
      timestamp: new Date(`2025-01-16T10:${i.toString().padStart(2, '0')}:00.000Z`),
      isOwnMessage: i % 2 === 0,
    }));

    render(<MessageList messages={manyMessages} />);

    // 最初と最後のメッセージが表示される
    expect(screen.getByText('メッセージ 1')).toBeInTheDocument();
    expect(screen.getByText('メッセージ 50')).toBeInTheDocument();

    // すべてのメッセージが存在する
    expect(screen.getAllByText(/メッセージ \d+/)).toHaveLength(50);
  });
});
