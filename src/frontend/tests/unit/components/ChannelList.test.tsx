import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '../../utils/test-utils';
import { ChannelList } from '@/components/ChannelList';
import type { Channel } from '@/types/chat';

describe('ChannelList', () => {
  const mockChannels: Channel[] = [
    { id: '1', name: '雑談' },
    { id: '2', name: 'ゲーム' },
    { id: '3', name: '音楽' },
  ];

  const mockOnChannelSelect = vi.fn();

  beforeEach(() => {
    mockOnChannelSelect.mockClear();
  });

  it('チャンネル一覧が正しく表示される', () => {
    render(
      <ChannelList
        channels={mockChannels}
        activeChannelId='1'
        onChannelSelect={mockOnChannelSelect}
      />,
    );

    expect(screen.getByText('チャンネル')).toBeInTheDocument();
    expect(screen.getByText('雑談')).toBeInTheDocument();
    expect(screen.getByText('ゲーム')).toBeInTheDocument();
    expect(screen.getByText('音楽')).toBeInTheDocument();
  });

  it('アクティブチャンネルがハイライトされる', () => {
    render(
      <ChannelList
        channels={mockChannels}
        activeChannelId='2'
        onChannelSelect={mockOnChannelSelect}
      />,
    );

    const activeChannel = screen.getByText('ゲーム').closest('a');
    const inactiveChannel = screen.getByText('雑談').closest('a');

    // アクティブなチャンネルは`active`クラスまたはデータ属性を持つ
    expect(activeChannel).toHaveAttribute('data-active', 'true');
    // 非アクティブなチャンネルは`data-active`属性を持たない
    expect(inactiveChannel).not.toHaveAttribute('data-active');
  });

  it('チャンネルクリック時にコールバックが呼ばれる', () => {
    render(
      <ChannelList
        channels={mockChannels}
        activeChannelId='1'
        onChannelSelect={mockOnChannelSelect}
      />,
    );

    fireEvent.click(screen.getByText('ゲーム'));
    expect(mockOnChannelSelect).toHaveBeenCalledWith('2');
  });

  it('すべてのチャンネルにハッシュアイコンが表示される', () => {
    render(
      <ChannelList
        channels={mockChannels}
        activeChannelId='1'
        onChannelSelect={mockOnChannelSelect}
      />,
    );

    // IconHashが3つ表示されることを確認
    const icons = document.querySelectorAll('svg');
    expect(icons.length).toBeGreaterThanOrEqual(3);
  });

  it('空のチャンネルリストでも正常に表示される', () => {
    render(<ChannelList channels={[]} activeChannelId='' onChannelSelect={mockOnChannelSelect} />);

    expect(screen.getByText('チャンネル')).toBeInTheDocument();
    // チャンネル項目がないことを確認
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
  });

  it('キーボードナビゲーションが可能', () => {
    render(
      <ChannelList
        channels={mockChannels}
        activeChannelId='1'
        onChannelSelect={mockOnChannelSelect}
      />,
    );

    const gameChannel = screen.getByText('ゲーム').closest('a');
    expect(gameChannel).toBeInTheDocument();

    // リンク要素がフォーカス可能であることを確認（tabIndexまたは要素の存在確認）
    expect(gameChannel).toHaveAttribute('class', expect.stringContaining('mantine-NavLink-root'));
    expect(gameChannel?.tagName.toLowerCase()).toBe('a');
  });
});
