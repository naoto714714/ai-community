import { Group, TextInput, ActionIcon } from '@mantine/core';
import { IconSend } from '@tabler/icons-react';
import { useState } from 'react';

interface MessageInputProps {
  onSendMessage: (content: string) => void;
}

export function MessageInput({ onSendMessage }: MessageInputProps) {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Group gap='sm' style={{ padding: '1rem' }}>
      <TextInput
        placeholder='メッセージを入力...'
        value={message}
        onChange={(e) => setMessage(e.currentTarget.value)}
        onKeyDown={handleKeyPress}
        maxLength={2000}
        style={{ flex: 1 }}
        size='md'
        radius='xl'
      />
      <ActionIcon
        onClick={handleSend}
        size='lg'
        radius='xl'
        variant='filled'
        disabled={!message.trim()}
      >
        <IconSend size='1.2rem' />
      </ActionIcon>
    </Group>
  );
}
