import { Stack, Box, Group, Title } from '@mantine/core';
import { IconHash } from '@tabler/icons-react';
import { MessageInput } from './MessageInput';
import { MessageList } from './MessageList';
import type { Message } from '../types/chat';
import { initialChannels } from '../data/channels';

interface ChatAreaProps {
  channelId: string;
  messages: Message[];
  onSendMessage: (content: string) => void;
}

export function ChatArea({ channelId, messages, onSendMessage }: ChatAreaProps) {
  const channelMessages = messages.filter((m) => m.channelId === channelId);
  const currentChannel = initialChannels.find((ch) => ch.id === channelId);

  return (
    <Stack h='100%' gap={0}>
      <Box p='md' style={{ borderBottom: '1px solid var(--mantine-color-gray-8)' }}>
        <Group>
          <IconHash size='1.5rem' />
          <Title order={3}>{currentChannel?.name}</Title>
        </Group>
      </Box>
      <Box style={{ flex: 1, overflow: 'hidden' }}>
        <MessageList messages={channelMessages} />
      </Box>
      <MessageInput onSendMessage={onSendMessage} />
    </Stack>
  );
}
