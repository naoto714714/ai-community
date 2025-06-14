# チャットアプリケーション段階的実装手順書

## はじめに
この手順書では、チャットアプリケーションを段階的に実装していきます。各ステップを完了してから次に進むことで、着実に機能を追加していけます。

---

## ステップ1: プロジェクトの初期セットアップ

### 1.1 プロジェクトの作成
```bash
# Viteを使用してReact + TypeScriptプロジェクトを作成
npm create vite@latest chat-app -- --template react-ts

# プロジェクトディレクトリに移動
cd chat-app

# 依存関係をインストール
npm install
```

### 1.2 Mantineと関連ライブラリのインストール
```bash
# Mantine UIライブラリのインストール
npm install @mantine/core @mantine/hooks

# アイコンライブラリのインストール
npm install @tabler/icons-react

# 日付処理用（タイムスタンプ表示）
npm install dayjs
```

### 1.3 Mantineの初期設定
`src/main.tsx`を編集：
```tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import { MantineProvider } from '@mantine/core'
import '@mantine/core/styles.css'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <MantineProvider defaultColorScheme="dark">
      <App />
    </MantineProvider>
  </React.StrictMode>,
)
```

### 1.4 基本的なCSSリセット
`src/index.css`を編集：
```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP', sans-serif;
}

#root {
  height: 100vh;
  overflow: hidden;
}
```

### 確認ポイント
- プロジェクトが正常に起動するか（`npm run dev`）
- Mantineのスタイルが適用されているか

---

## ステップ2: 基本レイアウトの構築

### 2.1 型定義の作成
`src/types/chat.ts`を作成：
```typescript
export interface Message {
  id: string;
  channelId: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: Date;
  isOwnMessage: boolean;
}

export interface Channel {
  id: string;
  name: string;
}
```

### 2.2 レイアウトコンポーネントの作成
`src/components/Layout.tsx`を作成：
```tsx
import { AppShell } from '@mantine/core';

export function Layout() {
  return (
    <AppShell
      navbar={{ width: 280, breakpoint: 'sm' }}
      padding="md"
    >
      <AppShell.Navbar p="md">
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
```

### 2.3 App.tsxの更新
```tsx
import { Layout } from './components/Layout';

function App() {
  return <Layout />;
}

export default App;
```

### 確認ポイント
- 左側にサイドバー、右側にメインエリアが表示されているか
- レイアウトが正しく分割されているか

---

## ステップ3: チャンネル一覧の実装

### 3.1 チャンネルデータの準備
`src/data/channels.ts`を作成：
```typescript
import { Channel } from '../types/chat';

export const initialChannels: Channel[] = [
  { id: '1', name: '雑談' },
  { id: '2', name: 'ゲーム' },
  { id: '3', name: '音楽' },
  { id: '4', name: '趣味' },
  { id: '5', name: 'ニュース' },
];
```

### 3.2 チャンネル一覧コンポーネントの作成
`src/components/ChannelList.tsx`を作成：
```tsx
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
    <Stack gap="xs">
      <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem' }}>チャンネル</h2>
      {channels.map((channel) => (
        <NavLink
          key={channel.id}
          active={activeChannelId === channel.id}
          label={channel.name}
          leftSection={<IconHash size="1.2rem" />}
          onClick={() => onChannelSelect(channel.id)}
          styles={{
            root: { borderRadius: '8px' },
          }}
        />
      ))}
    </Stack>
  );
}
```

### 3.3 Layoutコンポーネントの更新
```tsx
import { AppShell } from '@mantine/core';
import { useState } from 'react';
import { ChannelList } from './ChannelList';
import { initialChannels } from '../data/channels';

export function Layout() {
  const [activeChannelId, setActiveChannelId] = useState(initialChannels[0].id);

  return (
    <AppShell
      navbar={{ width: 280, breakpoint: 'sm' }}
      padding="md"
    >
      <AppShell.Navbar p="md">
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
```

### 確認ポイント
- チャンネル一覧が表示されているか
- チャンネルをクリックすると選択状態が変わるか
- アクティブなチャンネルがハイライトされているか

---

## ステップ4: メッセージ入力欄の実装

### 4.1 メッセージ入力コンポーネントの作成
`src/components/MessageInput.tsx`を作成：
```tsx
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
    <Group gap="sm" style={{ padding: '1rem' }}>
      <TextInput
        placeholder="メッセージを入力..."
        value={message}
        onChange={(e) => setMessage(e.currentTarget.value)}
        onKeyDown={handleKeyPress}
        maxLength={2000}
        style={{ flex: 1 }}
        size="md"
        radius="xl"
      />
      <ActionIcon
        onClick={handleSend}
        size="lg"
        radius="xl"
        variant="filled"
        disabled={!message.trim()}
      >
        <IconSend size="1.2rem" />
      </ActionIcon>
    </Group>
  );
}
```

### 4.2 チャット画面コンポーネントの作成
`src/components/ChatArea.tsx`を作成：
```tsx
import { Stack } from '@mantine/core';
import { MessageInput } from './MessageInput';

interface ChatAreaProps {
  channelId: string;
  onSendMessage: (content: string) => void;
}

export function ChatArea({ channelId, onSendMessage }: ChatAreaProps) {
  return (
    <Stack h="100%" justify="space-between">
      <div style={{ flex: 1, overflowY: 'auto', padding: '1rem' }}>
        {/* メッセージ一覧がここに入る */}
        <p>チャンネル {channelId} のメッセージエリア</p>
      </div>
      <MessageInput onSendMessage={onSendMessage} />
    </Stack>
  );
}
```

### 4.3 Layoutコンポーネントの更新
メッセージ送信のハンドラーを追加：
```tsx
const handleSendMessage = (content: string) => {
  console.log('送信されたメッセージ:', content);
  // TODO: メッセージを状態に追加
};

// AppShell.Mainの中を更新
<AppShell.Main>
  <ChatArea
    channelId={activeChannelId}
    onSendMessage={handleSendMessage}
  />
</AppShell.Main>
```

### 確認ポイント
- メッセージ入力欄が表示されているか
- Enterキーまたは送信ボタンでメッセージが送信されるか（コンソールで確認）
- 入力欄が2000文字で制限されているか

---

## ステップ5: メッセージ表示機能の実装

### 5.1 メッセージ表示コンポーネントの作成
`src/components/MessageItem.tsx`を作成：
```tsx
import { Box, Text, Group } from '@mantine/core';
import dayjs from 'dayjs';
import { Message } from '../types/chat';

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
        <Group justify="space-between" gap="xs" mb="xs">
          <Text size="sm" fw={600}>
            {message.userName}
          </Text>
          <Text size="xs" opacity={0.7}>
            {dayjs(message.timestamp).format('HH:mm')}
          </Text>
        </Group>
        <Text style={{ wordBreak: 'break-word' }}>
          {message.content}
        </Text>
      </Box>
    </Box>
  );
}
```

### 5.2 グローバルCSSにアニメーションを追加
`src/index.css`に追加：
```css
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

### 5.3 メッセージリストコンポーネントの作成
`src/components/MessageList.tsx`を作成：
```tsx
import { ScrollArea } from '@mantine/core';
import { Message } from '../types/chat';
import { MessageItem } from './MessageItem';
import { useEffect, useRef } from 'react';

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 新しいメッセージが追加されたら自動スクロール
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({
        top: scrollAreaRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);

  return (
    <ScrollArea h="100%" viewportRef={scrollAreaRef}>
      <div style={{ padding: '1rem' }}>
        {messages.length === 0 ? (
          <Text ta="center" c="dimmed">
            まだメッセージがありません
          </Text>
        ) : (
          messages.map((message) => (
            <MessageItem key={message.id} message={message} />
          ))
        )}
      </div>
    </ScrollArea>
  );
}
```

### 5.4 ChatAreaコンポーネントの更新
```tsx
import { Stack } from '@mantine/core';
import { MessageInput } from './MessageInput';
import { MessageList } from './MessageList';
import { Message } from '../types/chat';

interface ChatAreaProps {
  channelId: string;
  messages: Message[];
  onSendMessage: (content: string) => void;
}

export function ChatArea({ channelId, messages, onSendMessage }: ChatAreaProps) {
  const channelMessages = messages.filter(m => m.channelId === channelId);

  return (
    <Stack h="100%" gap={0}>
      <MessageList messages={channelMessages} />
      <MessageInput onSendMessage={onSendMessage} />
    </Stack>
  );
}
```

### 確認ポイント
- メッセージが正しく表示されるか
- 自分と他人のメッセージが色分けされているか
- フェードインアニメーションが動作するか
- 自動スクロールが機能するか

---

## ステップ6: メッセージ送信とbot返信機能の実装

### 6.1 Layoutコンポーネントの完成
`src/components/Layout.tsx`を最終的に更新：
```tsx
import { AppShell } from '@mantine/core';
import { useState, useCallback } from 'react';
import { ChannelList } from './ChannelList';
import { ChatArea } from './ChatArea';
import { initialChannels } from '../data/channels';
import { Message } from '../types/chat';

export function Layout() {
  const [activeChannelId, setActiveChannelId] = useState(initialChannels[0].id);
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSendMessage = useCallback((content: string) => {
    // ユーザーのメッセージを追加
    const userMessage: Message = {
      id: Date.now().toString(),
      channelId: activeChannelId,
      userId: 'user',
      userName: 'ユーザー',
      content,
      timestamp: new Date(),
      isOwnMessage: true,
    };

    setMessages(prev => [...prev, userMessage]);

    // 1秒後にbotが返信
    setTimeout(() => {
      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        channelId: activeChannelId,
        userId: 'bot',
        userName: 'bot',
        content: 'こんにちは',
        timestamp: new Date(),
        isOwnMessage: false,
      };
      setMessages(prev => [...prev, botMessage]);
    }, 1000);
  }, [activeChannelId]);

  return (
    <AppShell
      navbar={{ width: 280, breakpoint: 'sm' }}
      padding="md"
    >
      <AppShell.Navbar p="md" style={{ borderRight: '1px solid var(--mantine-color-gray-8)' }}>
        <ChannelList
          channels={initialChannels}
          activeChannelId={activeChannelId}
          onChannelSelect={setActiveChannelId}
        />
      </AppShell.Navbar>

      <AppShell.Main>
        <ChatArea
          channelId={activeChannelId}
          messages={messages}
          onSendMessage={handleSendMessage}
        />
      </AppShell.Main>
    </AppShell>
  );
}
```

### 6.2 MessageListコンポーネントのインポート修正
`src/components/MessageList.tsx`の先頭に追加：
```tsx
import { ScrollArea, Text } from '@mantine/core';
```

### 確認ポイント
- メッセージを送信すると画面に表示されるか
- 1秒後にbotから「こんにちは」と返信が来るか
- チャンネルを切り替えると、そのチャンネルのメッセージのみが表示されるか
- 絵文字（😊など）を入力して送信できるか

---

## ステップ7: 最終調整とスタイリング

### 7.1 ヘッダーの追加（オプション）
チャット画面の上部に現在のチャンネル名を表示：
`src/components/ChatArea.tsx`を更新：
```tsx
export function ChatArea({ channelId, messages, onSendMessage }: ChatAreaProps) {
  const channelMessages = messages.filter(m => m.channelId === channelId);
  const currentChannel = initialChannels.find(ch => ch.id === channelId);

  return (
    <Stack h="100%" gap={0}>
      <Box p="md" style={{ borderBottom: '1px solid var(--mantine-color-gray-8)' }}>
        <Group>
          <IconHash size="1.5rem" />
          <Title order={3}>{currentChannel?.name}</Title>
        </Group>
      </Box>
      <Box style={{ flex: 1, overflow: 'hidden' }}>
        <MessageList messages={channelMessages} />
      </Box>
      <MessageInput onSendMessage={onSendMessage} />
    </Stack>
  );
}
```

必要なインポートを追加：
```tsx
import { Stack, Box, Group, Title } from '@mantine/core';
import { IconHash } from '@tabler/icons-react';
import { initialChannels } from '../data/channels';
```

### 7.2 スクロールバーのスタイリング（オプション）
`src/index.css`に追加：
```css
/* カスタムスクロールバー */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: var(--mantine-color-gray-7);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: var(--mantine-color-gray-6);
}
```

### 最終確認ポイント
- すべての機能が正常に動作するか
- デザインがモダンでカジュアルな印象か
- アニメーションがスムーズか
- 2000文字の長文も正しく表示されるか

---

## 完成！

これで基本的なチャットアプリケーションが完成しました。

### 今後の拡張案
- メッセージの編集・削除機能
- 画像やファイルの送信
- ユーザーのオンライン状態表示
- メッセージの検索機能
- 通知機能
- バックエンドとの連携

### トラブルシューティング
1. **スタイルが適用されない場合**
   - `@mantine/core/styles.css`のインポートを確認
   - MantineProviderの設定を確認

2. **TypeScriptエラーが出る場合**
   - 型定義ファイルが正しく作成されているか確認
   - インポートパスが正しいか確認

3. **レイアウトが崩れる場合**
   - index.cssの設定を確認
   - AppShellコンポーネントの構造を確認