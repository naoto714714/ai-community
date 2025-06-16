# フロントエンド

## 技術スタック

- **React 18** + **TypeScript** + **Mantine UI**
- **Vite** (ビルドツール)
- **WebSocket** (リアルタイム通信)

## アーキテクチャ

```
Layout (メイン)
├── ChannelList (サイドバー)
└── ChatArea 
    ├── MessageList
    ├── MessageItem
    └── MessageInput
```

## 主要機能

- **チャンネル切り替え**: 左サイドバーで選択
- **メッセージ送受信**: WebSocketでリアルタイム通信
- **メッセージ履歴**: ページリロード時にREST APIで取得

## 開発

```bash
cd src/frontend
npm install
npm run dev  # http://localhost:5173
```

## 型定義

重要な型は `src/types/chat.ts` で管理：

```typescript
interface Message {
  id: string;
  channelId: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: Date;
  isOwnMessage: boolean;
}

interface Channel {
  id: string;
  name: string;
}
```