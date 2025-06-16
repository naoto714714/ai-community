# フロントエンド実装詳細

## 概要

AI Community フロントエンドは、React 18 + TypeScript + Mantine 7 を使用したモダンなチャットアプリケーションです。
WebSocket を使用してバックエンドとリアルタイム通信を行い、メッセージの送受信とチャンネル管理を実現しています。

## 技術構成

### コア技術
- **React**: 18.x (関数コンポーネント + Hooks)
- **TypeScript**: 5.x (型安全性の確保)
- **Mantine**: 7.x (UIコンポーネントライブラリ)
- **Vite**: ビルドツール・開発サーバー
- **WebSocket**: リアルタイム通信

### ライブラリ
- **@tabler/icons-react**: アイコンライブラリ
- **dayjs**: 日付処理
- **ESLint + Prettier**: コード品質管理

## プロジェクト構造

```
src/frontend/src/
├── components/          # Reactコンポーネント
│   ├── Layout.tsx      # アプリケーション全体のレイアウト
│   ├── ChannelList.tsx # チャンネル一覧
│   ├── ChatArea.tsx    # チャット画面全体
│   ├── MessageList.tsx # メッセージ一覧表示
│   ├── MessageItem.tsx # 個別メッセージ表示
│   └── MessageInput.tsx # メッセージ入力欄
├── types/              # TypeScript型定義
│   └── chat.ts         # Message, Channel型定義
├── data/              # 初期データ・設定
│   └── channels.ts    # 初期チャンネルデータ
├── App.tsx            # ルートコンポーネント
├── main.tsx           # エントリーポイント
└── index.css          # グローバルスタイル
```

## 型定義

### メッセージ型 (Message)

```typescript
export interface Message {
  id: string;          // 一意識別子
  channelId: string;   // 所属チャンネルID
  userId: string;      // 送信者ID
  userName: string;    // 送信者名
  content: string;     // メッセージ本文
  timestamp: Date;     // 送信時刻
  isOwnMessage: boolean; // 自分のメッセージかどうか
}
```

### チャンネル型 (Channel)

```typescript
export interface Channel {
  id: string;   // チャンネルID
  name: string; // チャンネル名
}
```

## コンポーネント詳細

### Layout.tsx (メインレイアウト)

アプリケーション全体のレイアウトと状態管理を担当するルートコンポーネント。

**主な責務:**
- WebSocket接続の管理
- アクティブチャンネルの状態管理
- メッセージ配列の状態管理
- チャンネル変更時のメッセージ履歴取得
- メッセージ送信処理

**状態管理:**
```typescript
const [activeChannelId, setActiveChannelId] = useState<string>('1');
const [messages, setMessages] = useState<Message[]>([]);
const wsRef = useRef<WebSocket | null>(null);
```

**WebSocket処理:**
- 接続：`ws://localhost:8000/ws`
- メッセージ送信：`message:send` タイプ
- 応答受信：`message:saved`, `message:error` タイプ

### ChannelList.tsx (チャンネル一覧)

左サイドバーのチャンネル一覧表示コンポーネント。

**特徴:**
- Mantine の `NavLink` コンポーネントを使用
- アクティブチャンネルのハイライト表示
- `IconHash` アイコンの表示
- クリックでチャンネル切り替え

### ChatArea.tsx (チャット画面)

メインエリアのチャット画面全体を管理するコンポーネント。

**構成:**
- チャンネル名ヘッダー
- メッセージ一覧 (`MessageList`)
- メッセージ入力欄 (`MessageInput`)

### MessageList.tsx (メッセージ一覧)

メッセージの一覧表示とスクロール管理を担当。

**特徴:**
- 新メッセージ追加時の自動スクロール
- メッセージのフェードインアニメーション
- `MessageItem` コンポーネントのレンダリング

### MessageItem.tsx (個別メッセージ)

個別メッセージの表示スタイリングを担当。

**表示内容:**
- ユーザー名
- メッセージ本文
- タイムスタンプ (HH:mm 形式)
- 自分/他人のメッセージによる色分け

### MessageInput.tsx (メッセージ入力)

メッセージ入力と送信機能を提供。

**機能:**
- テキスト入力 (最大2000文字)
- Enter キーでの送信
- 送信ボタンクリック
- 入力後のフィールドクリア

## データフロー

### 1. アプリケーション初期化
1. `Layout` コンポーネントでWebSocket接続を確立
2. 初期チャンネル（雑談）をアクティブに設定
3. アクティブチャンネルのメッセージ履歴をREST APIで取得

### 2. メッセージ送信フロー
1. ユーザーが `MessageInput` でメッセージを入力
2. `handleSendMessage` コールバックが実行
3. 新しい `Message` オブジェクトを作成
4. ローカル状態を即座に更新（オプティミスティックアップデート）
5. WebSocketでバックエンドに送信
6. バックエンドから保存確認/エラーレスポンスを受信

### 3. チャンネル切り替えフロー
1. ユーザーが `ChannelList` でチャンネルをクリック
2. `activeChannelId` 状態が更新
3. `useEffect` でチャンネル変更を検知
4. 新しいチャンネルのメッセージ履歴をREST APIで取得
5. `messages` 状態を新しいメッセージで更新

## API 連携

### REST API

**チャンネル一覧取得:**
```typescript
fetch('http://localhost:8000/api/channels')
```

**メッセージ履歴取得:**
```typescript
fetch(`http://localhost:8000/api/channels/${channelId}/messages`)
```

### WebSocket通信

**接続:**
```typescript
const ws = new WebSocket('ws://localhost:8000/ws');
```

**メッセージ送信:**
```typescript
const wsMessage = {
  type: 'message:send',
  data: {
    id: userMessage.id,
    channel_id: userMessage.channelId,
    user_id: userMessage.userId,
    user_name: userMessage.userName,
    content: userMessage.content,
    timestamp: userMessage.timestamp.toISOString(),
    is_own_message: userMessage.isOwnMessage,
  }
};
ws.send(JSON.stringify(wsMessage));
```

## スタイリング

### Mantine テーマシステム

- **カラーテーマ**: ダークモード対応
- **レイアウト**: `AppShell` コンポーネント
- **サイドバー幅**: 280px
- **レスポンシブ**: PC版優先（最小幅1024px）

### コンポーネントスタイル

**メッセージの色分け:**
- 自分のメッセージ: 青系背景
- 他人のメッセージ: グレー系背景

**アニメーション:**
- メッセージ送信時: フェードイン効果
- ホバー効果: ボタン・チャンネルリンク

## 設定ファイル

### package.json 主要依存関係

```json
{
  "dependencies": {
    "react": "^18.3.1",
    "@mantine/core": "^7.15.3",
    "@mantine/hooks": "^7.15.3",
    "@tabler/icons-react": "^3.26.0",
    "dayjs": "^1.11.13"
  },
  "devDependencies": {
    "@types/react": "^18.3.12",
    "typescript": "~5.6.2",
    "vite": "^6.0.1",
    "eslint": "^9.15.0"
  }
}
```

### Vite設定 (vite.config.ts)

- React plugin 設定
- 開発サーバー設定
- TypeScript設定

### TypeScript設定

- 厳密な型チェック
- React JSX サポート
- ES2020 ターゲット

## 開発ワークフロー

### 起動方法

```bash
cd src/frontend
npm install        # 依存関係インストール
npm run dev        # 開発サーバー起動 (http://localhost:5173)
```

### コード品質管理

```bash
npm run lint       # ESLint チェック
npm run build      # プロダクションビルド
npm run preview    # ビルド確認
```

### 開発時のベストプラクティス

1. **コンポーネント設計**: 小さく、再利用可能な単機能コンポーネント
2. **型安全性**: すべてのpropsとstateに型定義
3. **パフォーマンス**: `useCallback`, `useMemo` でレンダリング最適化
4. **エラーハンドリング**: WebSocketとAPI呼び出しのエラー処理
5. **アクセシビリティ**: Mantineコンポーネントの適切な使用

## 今後の拡張予定

### 近期実装候補
- [ ] メッセージ検索機能
- [ ] 絵文字リアクション
- [ ] メッセージ編集・削除
- [ ] ファイルアップロード
- [ ] タイピングインジケーター

### 長期実装候補
- [ ] ユーザー認証・プロフィール
- [ ] プライベートメッセージ
- [ ] スマートフォン対応
- [ ] 音声・ビデオ通話
- [ ] メッセージのエクスポート機能

## パフォーマンス考慮事項

### 現在の最適化
- React.memo によるコンポーネント最適化
- useCallback によるコールバック関数の最適化
- オプティミスティックアップデート（即座のUI更新）

### 将来の最適化予定
- 仮想スクロール（大量メッセージ対応）
- メッセージのページネーション
- 画像・ファイルの遅延読み込み
- Service Worker によるオフライン対応