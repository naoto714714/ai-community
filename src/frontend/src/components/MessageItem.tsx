import { Box, Text, Group } from '@mantine/core';
import dayjs from 'dayjs';
import type { Message } from '../types/chat';

interface MessageItemProps {
  message: Message;
}

export function MessageItem({ message }: MessageItemProps) {
  return (
    <Box
      style={{
        display: 'flex',
        justifyContent: message.isOwnMessage ? 'flex-end' : 'flex-start',
        marginBottom: '1rem',
      }}
    >
      <Box
        style={{
          maxWidth: '70%',
          backgroundColor: message.isOwnMessage
            ? 'var(--mantine-color-blue-6)'
            : 'var(--mantine-color-gray-7)',
          color: 'white',
          padding: '0.75rem 1rem',
          borderRadius: '12px',
          animation: 'fadeIn 0.3s ease-in',
        }}
      >
        <Group justify='space-between' gap='xs' mb='xs'>
          <Text size='sm' fw={600}>
            {message.userName}
          </Text>
          <Text size='xs' opacity={0.7}>
            {dayjs(message.timestamp).format('HH:mm')}
          </Text>
        </Group>
        <Text style={{ wordBreak: 'break-word' }}>{message.content}</Text>
      </Box>
    </Box>
  );
}
