import { AppShell } from '@mantine/core';

export function Layout() {
  return (
    <AppShell navbar={{ width: 280, breakpoint: 'sm' }} padding='md'>
      <AppShell.Navbar p='md'>
        {/* チャンネル一覧がここに入る */}
        <div>チャンネル一覧</div>
      </AppShell.Navbar>

      <AppShell.Main>
        {/* チャット画面がここに入る */}
        <div>チャット画面</div>
      </AppShell.Main>
    </AppShell>
  );
}
