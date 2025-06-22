import { Group, Textarea, ActionIcon } from '@mantine/core';
import { IconSend } from '@tabler/icons-react';
import { useState, useRef } from 'react';

interface MessageInputProps {
  onSendMessage: (content: string) => void;
}

export function MessageInput({ onSendMessage }: MessageInputProps) {
  const [message, setMessage] = useState('');
  const isComposingRef = useRef(false);
  const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
  const shortcutText = isMac ? '⌘+Enter' : 'Ctrl+Enter';

  const handleSend = () => {
    if (message.trim()) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    const correctModifier = isMac ? e.metaKey : e.ctrlKey;
    if (e.key === 'Enter' && correctModifier && !isComposingRef.current) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleCompositionStart = () => {
    isComposingRef.current = true;
  };

  const handleCompositionEnd = () => {
    isComposingRef.current = false;
  };

  return (
    <Group gap='sm' style={{ padding: '1.5rem 1.5rem 3rem 1.5rem' }}>
      <Textarea
        placeholder={`メッセージを入力... (${shortcutText}で送信)`}
        value={message}
        onChange={(e) => setMessage(e.currentTarget.value)}
        onKeyDown={handleKeyPress}
        onCompositionStart={handleCompositionStart}
        onCompositionEnd={handleCompositionEnd}
        maxLength={2000}
        style={{ flex: 1 }}
        size='md'
        radius='xl'
        minRows={1}
        maxRows={5}
        autosize
      />
      <ActionIcon
        onClick={handleSend}
        size='lg'
        radius='xl'
        variant='filled'
        disabled={!message.trim()}
        data-testid='send-button'
      >
        <IconSend size='1.2rem' />
      </ActionIcon>
    </Group>
  );
}
