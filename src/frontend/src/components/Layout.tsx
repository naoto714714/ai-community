import { AppShell } from '@mantine/core';
import { useState } from 'react';
import { ChannelList } from './ChannelList';
import { initialChannels } from '../data/channels';

export function Layout() {
  const [activeChannelId, setActiveChannelId] = useState(initialChannels[0].id);

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
        <div>チャット画面 - チャンネルID: {activeChannelId}</div>
      </AppShell.Main>
    </AppShell>
  );
}
