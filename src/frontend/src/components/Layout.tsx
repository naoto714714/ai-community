import { AppShell } from '@mantine/core';
import { useState, useCallback } from 'react';
import { ChannelList } from './ChannelList';
import { ChatArea } from './ChatArea';
import { initialChannels } from '../data/channels';
import type { Message } from '../types/chat';

export function Layout() {
  const [activeChannelId, setActiveChannelId] = useState(
    initialChannels.length > 0 ? initialChannels[0].id : '',
  );
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSendMessage = useCallback(
    (content: string) => {
      // ユーザーのメッセージを追加
      const userMessage: Message = {
        id: Date.now().toString(),
        channelId: activeChannelId,
        userId: 'user',
        userName: 'ユーザー',
        content,
        timestamp: new Date(),
        isOwnMessage: true,
      };

      setMessages((prev) => [...prev, userMessage]);

      // 1秒後にbotが返信
      setTimeout(() => {
        const botMessage: Message = {
          id: (Date.now() + 1).toString(),
          channelId: activeChannelId,
          userId: 'bot',
          userName: 'bot',
          content: 'こんにちは',
          timestamp: new Date(),
          isOwnMessage: false,
        };
        setMessages((prev) => [...prev, botMessage]);
      }, 1000);
    },
    [activeChannelId],
  );

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
