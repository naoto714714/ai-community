import { Stack } from '@mantine/core';
import { MessageInput } from './MessageInput';
import { MessageList } from './MessageList';
import { Message } from '../types/chat';

interface ChatAreaProps {
  channelId: string;
  messages: Message[];
  onSendMessage: (content: string) => void;
}

export function ChatArea({ channelId, messages, onSendMessage }: ChatAreaProps) {
  const channelMessages = messages.filter((m) => m.channelId === channelId);

  return (
    <Stack h='100%' gap={0}>
      <MessageList messages={channelMessages} />
      <MessageInput onSendMessage={onSendMessage} />
    </Stack>
  );
}
