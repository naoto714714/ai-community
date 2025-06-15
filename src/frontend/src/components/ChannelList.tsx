import { Stack, NavLink } from '@mantine/core';
import { IconHash } from '@tabler/icons-react';
import { Channel } from '../types/chat';

interface ChannelListProps {
  channels: Channel[];
  activeChannelId: string;
  onChannelSelect: (channelId: string) => void;
}

export function ChannelList({ channels, activeChannelId, onChannelSelect }: ChannelListProps) {
  return (
    <Stack gap='xs'>
      <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>チャンネル</h2>
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
