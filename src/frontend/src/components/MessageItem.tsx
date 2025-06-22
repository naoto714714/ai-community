import { Box, Text, Group, Badge } from '@mantine/core';
import dayjs from 'dayjs';
import type { Message } from '../types/chat';

interface MessageItemProps {
  message: Message;
}

export function MessageItem({ message }: MessageItemProps) {
  const isAI = message.userType === 'ai';

  return (
    <Box
      data-testid='message-container'
      style={{
        display: 'flex',
        justifyContent: message.isOwnMessage ? 'flex-end' : 'flex-start',
        marginBottom: '1rem',
      }}
    >
      <Box
        data-testid='message-bubble'
        style={{
          maxWidth: '70%',
          backgroundColor: message.isOwnMessage
            ? 'var(--mantine-color-blue-6)'
            : isAI
              ? 'var(--mantine-color-violet-6)'
              : 'var(--mantine-color-gray-7)',
          color: 'white',
          padding: '0.75rem 1rem',
          borderRadius: '12px',
          animation: 'fadeIn 0.3s ease-in',
        }}
      >
        <Group justify='space-between' gap='xs' mb='xs'>
          <Group gap='xs'>
            <Text size='sm' fw={600}>
              {message.userName}
            </Text>
            {isAI && (
              <Badge size='xs' variant='light' color='violet'>
                AI
              </Badge>
            )}
          </Group>
          <Text size='xs' opacity={0.7}>
            {dayjs(message.timestamp).format('HH:mm')}
          </Text>
        </Group>
        <Text style={{ wordBreak: 'break-word' }}>{message.content}</Text>
      </Box>
    </Box>
  );
}
