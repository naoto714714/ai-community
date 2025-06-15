import { Stack, NavLink, Title } from '@mantine/core';
import { IconHash } from '@tabler/icons-react';

import type { Channel } from '../types/chat';

interface ChannelListProps {
  channels: Channel[];
  activeChannelId: string;
  onChannelSelect: (channelId: string) => void;
}

export function ChannelList({ channels, activeChannelId, onChannelSelect }: ChannelListProps) {
  return (
    <Stack gap='xs'>
      <Title order={3} mb='md'>
        チャンネル
      </Title>
      {channels.map((channel) => (
        <NavLink
          key={channel.id}
          active={activeChannelId === channel.id}
          label={channel.name}
          leftSection={<IconHash size='1.2rem' />}
          onClick={() => onChannelSelect(channel.id)}
          styles={{
            root: { borderRadius: '8px' },
          }}
        />
      ))}
    </Stack>
  );
}
