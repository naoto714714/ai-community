# AI Community Frontend

React + TypeScript + Mantineによるモダンなリアルタイムチャットアプリケーション

## 🚀 クイックスタート

```bash
# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
```

フロントエンドURL: `http://localhost:5173`

## 📁 プロジェクト構造

```
src/frontend/
├── src/
│   ├── App.tsx          # メインアプリケーション
│   ├── main.tsx         # エントリーポイント
│   ├── index.css        # グローバルスタイル
│   ├── components/      # Reactコンポーネント
│   │   ├── Layout.tsx   # アプリケーションレイアウト
│   │   ├── ChannelList.tsx
│   │   ├── ChatArea.tsx
│   │   ├── MessageList.tsx
│   │   ├── MessageItem.tsx
│   │   └── MessageInput.tsx
│   ├── types/           # TypeScript型定義
│   │   └── chat.ts
│   └── data/            # 初期データ
│       └── channels.ts
├── package.json         # NPM設定
├── tsconfig.json        # TypeScript設定
├── vite.config.ts       # Vite設定
└── eslint.config.js     # ESLint設定
```

## 🔧 技術スタック

- **React**: 18.x
- **TypeScript**: 5.x
- **Mantine**: 7.x (UIライブラリ)
- **Tabler Icons**: アイコンライブラリ
- **Vite**: ビルドツール・開発サーバー
- **dayjs**: 日付処理
- **ESLint**: コード品質管理

## 🎨 デザインシステム

### UIコンポーネント

- **Mantine**をベースとしたコンポーネント設計
- ダークモード対応
- レスポンシブデザイン（PC優先）

### レイアウト

- 左サイドバー（280px）: チャンネル一覧
- メインエリア: チャット画面
- 最小幅: 1024px

### カラーテーマ

- アクセントカラー: blue/violet系
- システムフォント優先

## 🔨 開発ルール

### コンポーネント設計

- 関数コンポーネント + TypeScript
- Props型定義必須
- 単一責任の原則
- Mantineコンポーネント優先使用

### 状態管理

- React Hooks（useState, useEffect）
- カスタムフックでロジック分離
- 将来的にContext API追加予定

### スタイリング

- Mantineテーマシステム
- CSS-in-JSアプローチ
- グローバルCSS最小限

### TypeScript

- 厳密な型チェック
- interface/type定義
- Propdrillは最小限

## 🔍 開発コマンド

```bash
# 開発サーバー起動
npm run dev

# プロダクションビルド
npm run build

# ビルド結果プレビュー
npm run preview

# ESLintチェック
npm run lint
```

## 📋 実装済み機能

- ✅ Vite + React + TypeScript環境
- ✅ Mantine UIライブラリ統合
- ✅ AppShellレイアウト
- ✅ チャンネル一覧表示
- ✅ メッセージ一覧表示
- ✅ メッセージ入力・送信
- ✅ WebSocket通信
- ✅ リアルタイムメッセージ受信
- ✅ ダークモード対応
- ✅ レスポンシブ対応
- ✅ ESLint設定

## 🔗 バックエンド連携

### REST API

- チャンネル一覧取得: `GET /api/channels`
- メッセージ履歴取得: `GET /api/channels/{channel_id}/messages`

### WebSocket

- エンドポイント: `ws://localhost:8000/ws`
- メッセージ送信・受信
- リアルタイム通信

## 📱 今後の拡張予定

- [ ] ユーザー認証機能
- [ ] メッセージ検索
- [ ] ファイルアップロード
- [ ] 絵文字リアクション
- [ ] プッシュ通知
