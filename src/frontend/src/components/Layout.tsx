import { AppShell } from '@mantine/core';
import { useState } from 'react';
import { ChannelList } from './ChannelList';
import { ChatArea } from './ChatArea';
import { initialChannels } from '../data/channels';

export function Layout() {
  const [activeChannelId, setActiveChannelId] = useState(
    initialChannels.length > 0 ? initialChannels[0].id : '',
  );

  const handleSendMessage = (content: string) => {
    console.log('送信されたメッセージ:', content);
    // TODO: メッセージを状態に追加
  };

  return (
    <AppShell navbar={{ width: 280, breakpoint: 'sm' }} padding='md'>
      <AppShell.Navbar p='md'>
        <ChannelList
          channels={initialChannels}
          activeChannelId={activeChannelId}
          onChannelSelect={setActiveChannelId}
        />
      </AppShell.Navbar>

      <AppShell.Main>
        <ChatArea channelId={activeChannelId} onSendMessage={handleSendMessage} />
      </AppShell.Main>
    </AppShell>
  );
}
