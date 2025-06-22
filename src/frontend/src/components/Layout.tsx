import { AppShell, Burger } from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { nanoid } from 'nanoid';
import { ChannelList } from './ChannelList';
import { ChatArea } from './ChatArea';
import { initialChannels } from '../data/channels';
import type { Message, MessageResponse } from '../types/chat';
import { API_CONFIG, WEBSOCKET_CONFIG } from '../config/constants';

export function Layout() {
  const [opened, { toggle, close }] = useDisclosure();
  const [activeChannelId, setActiveChannelId] = useState(
    initialChannels.length > 0 ? initialChannels[0].id : '',
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const retryTimeoutRef = useRef<number | null>(null);
  const retryCountRef = useRef(0);

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
        await fetch(API_CONFIG.BASE_URL);

        const ws = new WebSocket(API_CONFIG.WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
          // 接続成功時は再試行カウントをリセット
          retryCountRef.current = 0;
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);

            if (data.type === 'message:saved') {
              // メッセージ保存成功 - 特に処理不要（楽観的更新のため）
            } else if (data.type === 'message:error') {
              console.error('Message save error:', data.data);
              // 送信失敗時のロールバック処理
              if (data.data?.id) {
                setMessages((prev) => prev.filter((msg) => msg.id !== data.data.id));
              }
            } else if (data.type === 'message:broadcast') {
              // 新しいメッセージ（ユーザーメッセージまたはAI応答）をリアルタイムで追加
              if (data.data) {
                const newMessage: Message = {
                  id: data.data.id,
                  channelId: data.data.channel_id,
                  userId: data.data.user_id,
                  userName: data.data.user_name,
                  userType: data.data.user_type || 'user', // デフォルトはuser
                  content: data.data.content,
                  timestamp: new Date(data.data.timestamp),
                  isOwnMessage: data.data.is_own_message,
                };

                // 重複チェック：同じIDのメッセージが既に存在する場合は追加しない
                setMessages((prev) => {
                  if (prev.some((msg) => msg.id === newMessage.id)) {
                    return prev;
                  }
                  return [...prev, newMessage];
                });
              }
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error, 'Raw data:', event.data);
          }
        };

        ws.onclose = (event) => {
          // 接続が予期せず閉じられた場合の再接続処理
          if (!event.wasClean && retryCountRef.current < WEBSOCKET_CONFIG.MAX_RETRY_COUNT) {
            console.log(
              `WebSocket disconnected unexpectedly. Retry ${retryCountRef.current + 1}/${WEBSOCKET_CONFIG.MAX_RETRY_COUNT}`,
            );
            retryCountRef.current += 1;
            retryTimeoutRef.current = window.setTimeout(
              connectWebSocket,
              WEBSOCKET_CONFIG.RETRY_DELAY_MS,
            );
          }
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };
      } catch (error) {
        console.error('Failed to connect to backend:', error);

        // 最大再試行回数に達していない場合のみ再試行
        if (retryCountRef.current < WEBSOCKET_CONFIG.MAX_RETRY_COUNT) {
          retryCountRef.current += 1;
          retryTimeoutRef.current = window.setTimeout(
            connectWebSocket,
            WEBSOCKET_CONFIG.RETRY_DELAY_MS,
          );
        } else {
          console.error('Max retry count reached. WebSocket connection failed.');
        }
      }
    };

    connectWebSocket();

    return () => {
      // クリーンアップ
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (retryTimeoutRef.current) {
        window.clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);

  // チャンネル変更時にメッセージ履歴を取得
  useEffect(() => {
    if (activeChannelId) {
      fetch(`${API_CONFIG.BASE_URL}/api/channels/${activeChannelId}/messages`)
        .then((res) => res.json())
        .then((data) => {
          // バックエンドから取得したメッセージを適合させる
          // PydanticスキーマでcamelCaseに変換されているため、camelCaseで参照
          const adaptedMessages: Message[] = data.messages.map((msg: MessageResponse) => ({
            id: msg.id,
            channelId: msg.channelId,
            userId: msg.userId,
            userName: msg.userName,
            userType: msg.userType || 'user', // デフォルトはuser
            content: msg.content,
            timestamp: new Date(msg.timestamp),
            isOwnMessage: msg.isOwnMessage,
          }));
          setMessages(adaptedMessages);
        })
        .catch((err) => console.error('Error loading messages:', err));
    }
  }, [activeChannelId]);

  const handleChannelSelect = useCallback(
    (channelId: string) => {
      setActiveChannelId(channelId);
      close(); // モバイル時にナビゲーションを閉じる
    },
    [close],
  );

  const handleSendMessage = useCallback(
    (content: string) => {
      // nanoidを使用してより安全で標準的なID生成
      const messageId = nanoid();

      const userMessage: Message = {
        id: messageId,
        channelId: activeChannelId,
        userId: 'user',
        userName: 'ユーザー',
        userType: 'user',
        content,
        timestamp: new Date(),
        isOwnMessage: true,
      };

      // ローカルステートを即座に更新（楽観的更新）
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
            user_type: userMessage.userType,
            content: userMessage.content,
            timestamp: userMessage.timestamp.toISOString(),
            is_own_message: userMessage.isOwnMessage,
          },
        };

        try {
          wsRef.current.send(JSON.stringify(wsMessage));
        } catch (error) {
          console.error('Failed to send message via WebSocket:', error);
          // 送信失敗時のロールバック
          setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id));
        }
      } else {
        console.error('WebSocket is not connected');
        // WebSocket未接続時のロールバック
        setMessages((prev) => prev.filter((msg) => msg.id !== userMessage.id));
      }
    },
    [activeChannelId],
  );

  return (
    <AppShell
      navbar={{
        width: 280,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      header={{ height: { base: 50, md: 0 } }}
      padding='md'
    >
      <AppShell.Header p='sm' hiddenFrom='md'>
        <Burger opened={opened} onClick={toggle} size='sm' />
      </AppShell.Header>

      <AppShell.Navbar p='md'>
        <ChannelList
          channels={initialChannels}
          activeChannelId={activeChannelId}
          onChannelSelect={handleChannelSelect}
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
