import { ScrollArea, Text } from '@mantine/core';
import type { Message } from '../types/chat';
import { MessageItem } from './MessageItem';
import { useEffect, useRef } from 'react';

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 新しいメッセージが追加されたら自動スクロール
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({
        top: scrollAreaRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);

  return (
    <ScrollArea h='100%' viewportRef={scrollAreaRef}>
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
