import { describe, it, expect, vi, beforeAll, afterAll } from 'vitest';
import { render, screen } from '../../utils/test-utils';
import { MessageList } from '@/components/MessageList';
import type { Message } from '@/types/chat';
import { createMockMessage } from '../../factories';

// scrollToのモック
const mockScrollTo = vi.fn();
let originalScrollTo: typeof HTMLElement.prototype.scrollTo;

describe('MessageList', () => {
  beforeAll(() => {
    // scrollToのスタブを設定（HTMLDivElementに対して）
    originalScrollTo = HTMLElement.prototype.scrollTo;
    Object.defineProperty(HTMLElement.prototype, 'scrollTo', {
      value: mockScrollTo,
      writable: true,
    });

    // scrollHeightのモックも設定
    Object.defineProperty(HTMLElement.prototype, 'scrollHeight', {
      value: 1000,
      configurable: true,
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
    createMockMessage({
      id: 'msg-1',
      channelId: '1',
      userId: 'user-1',
      userName: 'ユーザー1',
      content: 'こんにちは！',
      timestamp: new Date('2025-01-16T10:00:00.000Z'),
      isOwnMessage: false,
    }),
    createMockMessage({
      id: 'msg-2',
      channelId: '1',
      userId: 'user-2',
      userName: 'ユーザー2',
      content: 'お疲れ様です',
      timestamp: new Date('2025-01-16T10:01:00.000Z'),
      isOwnMessage: true,
    }),
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
    const setTimeoutSpy = vi.spyOn(window, 'setTimeout');
    const { rerender } = render(<MessageList messages={[mockMessages[0]]} />);

    // 最初のレンダリング後のタイマー設定を確認
    expect(setTimeoutSpy).toHaveBeenCalled();
    setTimeoutSpy.mockClear();

    // メッセージを追加
    rerender(<MessageList messages={mockMessages} />);

    // 新しいタイマーが設定されることを確認
    expect(setTimeoutSpy).toHaveBeenCalledWith(expect.any(Function), 100);

    setTimeoutSpy.mockRestore();
  });

  it('スクロール動作が正しく設定される', async () => {
    const setTimeoutSpy = vi.spyOn(window, 'setTimeout');

    render(<MessageList messages={mockMessages} />);

    // 100ms後にスクロール関数が実行されるタイマーが設定されることを確認
    expect(setTimeoutSpy).toHaveBeenCalledWith(expect.any(Function), 100);

    setTimeoutSpy.mockRestore();
  });

  it('メッセージの更新時に既存のタイマーがクリアされる', async () => {
    const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout');
    const { rerender } = render(<MessageList messages={[mockMessages[0]]} />);

    // メッセージを更新（これにより既存のタイマーがクリアされ、新しいタイマーが設定される）
    rerender(<MessageList messages={mockMessages} />);

    // clearTimeoutが呼ばれることを確認
    expect(clearTimeoutSpy).toHaveBeenCalled();

    clearTimeoutSpy.mockRestore();
  });

  it('コンポーネントアンマウント時にタイマーがクリアされる', () => {
    const clearTimeoutSpy = vi.spyOn(window, 'clearTimeout');
    const { unmount } = render(<MessageList messages={mockMessages} />);

    unmount();

    expect(clearTimeoutSpy).toHaveBeenCalled();
  });

  it('ScrollAreaが正しく設定される', () => {
    render(<MessageList messages={mockMessages} />);

    // ScrollAreaコンポーネントが存在する（Mantineのクラス名で確認）
    const scrollArea = document.querySelector('.mantine-ScrollArea-root');
    expect(scrollArea).toBeInTheDocument();

    // 高さが100%に設定されている
    expect(scrollArea).toHaveStyle('height: 100%');
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
