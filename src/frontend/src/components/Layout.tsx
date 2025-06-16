import { AppShell } from '@mantine/core';
import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { ChannelList } from './ChannelList';
import { ChatArea } from './ChatArea';
import { initialChannels } from '../data/channels';
import type { Message } from '../types/chat';

export function Layout() {
  const [activeChannelId, setActiveChannelId] = useState(
    initialChannels.length > 0 ? initialChannels[0].id : '',
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const currentChannel = useMemo(
    () => initialChannels.find((ch) => ch.id === activeChannelId),
    [activeChannelId],
  );

  // WebSocket接続の初期化
  useEffect(() => {
    // バックエンドの起動を待ってからWebSocket接続
    const connectWebSocket = async () => {
      try {
        // バックエンドの動作確認
        await fetch('http://localhost:8000/');
        console.log('Backend is ready, connecting WebSocket...');

        const ws = new WebSocket('ws://localhost:8000/ws');
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('WebSocket connected');
        };

        ws.onmessage = (event) => {
          const data = JSON.parse(event.data);
          console.log('WebSocket message received:', data);

          if (data.type === 'message:saved') {
            console.log('Message saved confirmation:', data.data);
          } else if (data.type === 'message:error') {
            console.error('Message save error:', data.data);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket disconnected');
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (error) {
        console.error('Failed to connect to backend:', error);
        // 3秒後に再試行
        setTimeout(connectWebSocket, 3000);
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // チャンネル変更時にメッセージ履歴を取得
  useEffect(() => {
    if (activeChannelId) {
      fetch(`http://localhost:8000/api/channels/${activeChannelId}/messages`)
        .then((res) => res.json())
        .then((data) => {
          console.log('Loaded messages:', data);
          console.log('Messages array length:', data.messages?.length || 0);
          console.log('First message:', data.messages?.[0]);
          // バックエンドから取得したメッセージを適合させる
          // PydanticスキーマでcamelCaseに変換されているため、camelCaseで参照
          const adaptedMessages: Message[] = data.messages.map(
            (msg: {
              id: string;
              channelId: string;
              userId: string;
              userName: string;
              content: string;
              timestamp: string;
              isOwnMessage: boolean;
            }) => ({
              id: msg.id,
              channelId: msg.channelId,
              userId: msg.userId,
              userName: msg.userName,
              content: msg.content,
              timestamp: new Date(msg.timestamp),
              isOwnMessage: msg.isOwnMessage,
            }),
          );
          console.log('Adapted messages:', adaptedMessages);
          console.log('Setting messages state with', adaptedMessages.length, 'messages');
          setMessages(adaptedMessages);
        })
        .catch((err) => console.error('Error loading messages:', err));
    }
  }, [activeChannelId]);

  const handleSendMessage = useCallback(
    (content: string) => {
      const userMessage: Message = {
        id: Date.now().toString(),
        channelId: activeChannelId,
        userId: 'user',
        userName: 'ユーザー',
        content,
        timestamp: new Date(),
        isOwnMessage: true,
      };

      // ローカルステートを即座に更新
      setMessages((prev) => [...prev, userMessage]);

      // WebSocketでバックエンドに送信
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        const wsMessage = {
          type: 'message:send',
          data: {
            id: userMessage.id,
            channel_id: userMessage.channelId,
            user_id: userMessage.userId,
            user_name: userMessage.userName,
            content: userMessage.content,
            timestamp: userMessage.timestamp.toISOString(),
            is_own_message: userMessage.isOwnMessage,
          },
        };

        wsRef.current.send(JSON.stringify(wsMessage));
      }
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
          currentChannel={currentChannel}
          messages={messages}
          onSendMessage={handleSendMessage}
        />
      </AppShell.Main>
    </AppShell>
  );
}
