import { Stack, Box, Group, Title } from '@mantine/core';
import { IconHash } from '@tabler/icons-react';
import { MessageInput } from './MessageInput';
import { MessageList } from './MessageList';
import type { Message, Channel } from '../types/chat';

interface ChatAreaProps {
  channelId: string;
  currentChannel: Channel | undefined;
  messages: Message[];
  onSendMessage: (content: string) => void;
}

export function ChatArea({ channelId, currentChannel, messages, onSendMessage }: ChatAreaProps) {
  const channelMessages = messages.filter((m) => m.channelId === channelId);

  return (
    <Stack h='100vh' gap={0} style={{ position: 'relative' }}>
      <Box p='md' style={{ borderBottom: '1px solid var(--mantine-color-gray-8)', flexShrink: 0 }}>
        <Group>
          <IconHash size='1.5rem' />
          <Title order={3}>{currentChannel?.name ?? 'チャンネルが見つかりません'}</Title>
        </Group>
      </Box>
      <Box style={{ flex: 1, overflow: 'hidden', paddingBottom: '100px' }}>
        <MessageList messages={channelMessages} />
      </Box>
      <Box
        style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0,
          backgroundColor: 'var(--mantine-color-dark-7)',
          borderTop: '1px solid var(--mantine-color-gray-8)',
          zIndex: 10,
        }}
      >
        <MessageInput onSendMessage={onSendMessage} />
      </Box>
    </Stack>
  );
}
