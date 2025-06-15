import { Stack } from '@mantine/core';
import { MessageInput } from './MessageInput';

interface ChatAreaProps {
  channelId: string;
  onSendMessage: (content: string) => void;
}

export function ChatArea({ channelId, onSendMessage }: ChatAreaProps) {
  return (
    <Stack h='100%' justify='space-between'>
      <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
        {/* メッセージ一覧がここに入る */}
        <p>チャンネル {channelId} のメッセージエリア</p>
      </div>
      <MessageInput onSendMessage={onSendMessage} />
    </Stack>
  );
}
