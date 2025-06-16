import { ScrollArea, Text } from '@mantine/core';
import type { Message } from '../types/chat';
import { MessageItem } from './MessageItem';
import { useEffect, useRef } from 'react';

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  const viewport = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    if (viewport.current) {
      viewport.current.scrollTo({
        top: viewport.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  };

  useEffect(() => {
    // メッセージが変更されたら少し遅延してスクロール
    const timer = setTimeout(scrollToBottom, 100);
    return () => clearTimeout(timer);
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
