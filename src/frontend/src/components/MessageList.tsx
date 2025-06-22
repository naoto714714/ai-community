import { ScrollArea, Text } from '@mantine/core';
import type { Message } from '../types/chat';
import { MessageItem } from './MessageItem';
import { useEffect, useRef } from 'react';
import { MESSAGE_CONFIG } from '../config/constants';

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  const viewport = useRef<HTMLDivElement>(null);
  const scrollTimerRef = useRef<number | null>(null);

  const scrollToBottom = () => {
    if (viewport.current) {
      viewport.current.scrollTo({
        top: viewport.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  };

  useEffect(() => {
    // 既存のタイマーをクリア
    if (scrollTimerRef.current) {
      window.clearTimeout(scrollTimerRef.current);
    }

    // メッセージが変更されたら少し遅延してスクロール
    scrollTimerRef.current = window.setTimeout(scrollToBottom, MESSAGE_CONFIG.SCROLL_DELAY_MS);

    return () => {
      if (scrollTimerRef.current) {
        window.clearTimeout(scrollTimerRef.current);
      }
    };
  }, [messages]);

  return (
    <ScrollArea h='100%' viewportRef={viewport}>
      <div style={{ padding: '1rem' }}>
        {messages.length === 0 ? (
          <Text ta='center' c='dimmed'>
            まだメッセージがありません
          </Text>
        ) : (
          messages.map((message) => <MessageItem key={message.id} message={message} />)
        )}
      </div>
    </ScrollArea>
  );
}
