import { AppShell } from '@mantine/core';
import { useState } from 'react';
import { ChannelList } from './ChannelList';
import { ChatArea } from './ChatArea';
import { initialChannels } from '../data/channels';
import type { Message } from '../types/chat';

export function Layout() {
  const [activeChannelId, setActiveChannelId] = useState(
    initialChannels.length > 0 ? initialChannels[0].id : '',
  );
  const [messages, setMessages] = useState<Message[]>([
    // テスト用のダミーメッセージ
    {
      id: '1',
      channelId: '1',
      userId: 'user1',
      userName: 'ユーザー',
      content: 'こんにちは！',
      timestamp: new Date(Date.now() - 60000),
      isOwnMessage: true,
    },
    {
      id: '2',
      channelId: '1',
      userId: 'bot',
      userName: 'bot',
      content: 'こんにちは',
      timestamp: new Date(Date.now() - 30000),
      isOwnMessage: false,
    },
  ]);

  const handleSendMessage = (content: string) => {
    console.log('送信されたメッセージ:', content);
    // TODO: メッセージを状態に追加（ステップ6で実装予定）
    // 以下のようにsetMessagesを使用予定:
    // setMessages(prev => [...prev, newMessage]);

    // 一時的にsetMessagesを参照してESLintエラーを回避
    void setMessages;
  };

  return (
    <AppShell navbar={{ width: 280, breakpoint: 'sm' }} padding='md'>
      <AppShell.Navbar p='md'>
        <ChannelList
          channels={initialChannels}
          activeChannelId={activeChannelId}
          onChannelSelect={setActiveChannelId}
        />
      </AppShell.Navbar>

      <AppShell.Main>
        <ChatArea
          channelId={activeChannelId}
          messages={messages}
          onSendMessage={handleSendMessage}
        />
      </AppShell.Main>
    </AppShell>
  );
}
