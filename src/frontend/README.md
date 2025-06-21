# AI Community フロントエンド（Frontend）

React + TypeScript + Mantineによるモダンなリアルタイムチャットアプリケーション

## 🚀 クイックスタート

### 1. バックエンドサーバーを起動

**⚠️ 重要:** フロントエンドを起動する前に、バックエンドサーバーが起動している必要があります。

```bash
# バックエンドディレクトリに移動
cd ../backend

# バックエンドサーバー起動
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. フロントエンドを起動

```bash
# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
```

**アプリケーションURL:** [http://localhost:5173](http://localhost:5173)
**バックエンドAPI:** [http://localhost:8000](http://localhost:8000)

## 📁 プロジェクト構造

```text
src/frontend/
├── src/
│   ├── App.tsx              # メインアプリケーション
│   ├── main.tsx             # エントリーポイント
│   ├── index.css            # グローバルスタイル
│   ├── components/          # Reactコンポーネント
│   │   ├── Layout.tsx       # アプリケーションレイアウト
│   │   ├── ChannelList.tsx  # チャンネル一覧
│   │   ├── ChatArea.tsx     # チャット画面
│   │   ├── MessageList.tsx  # メッセージ一覧
│   │   ├── MessageItem.tsx  # メッセージ表示
│   │   └── MessageInput.tsx # メッセージ入力
│   ├── types/               # TypeScript型定義
│   │   └── chat.ts          # Message, Channel型
│   └── data/                # 初期データ
│       └── channels.ts      # 初期チャンネルデータ
├── package.json             # NPM設定
├── tsconfig.json            # TypeScript設定
├── vite.config.ts           # Vite設定
└── eslint.config.js         # ESLint設定
```

## 🔧 技術スタック

- **React:** 18.x
- **TypeScript:** 5.x
- **Mantine:** 7.x（UIライブラリ）
- **Tabler Icons:** アイコンライブラリ
- **Vite:** ビルドツール・開発サーバー
- **dayjs:** 日付処理
- **ESLint:** コード品質管理

## 📱 コンポーネント構造

### Layout.tsx（メインレイアウト）

- **WebSocket接続管理**: サーバーとの双方向通信を制御
- **アクティブチャンネル状態管理**: 現在選択中のチャンネル情報を保持
- **モバイルナビゲーション制御**: レスポンシブ対応のサイドバー表示切替
- **メッセージ送信処理**: ユーザー入力をWebSocket経由で送信

### MessageInput.tsx（メッセージ入力）

- **日本語IME対応**: Enter送信時の変換中防止でUX向上
- **最大2000文字制限**: 長文投稿の制御とバリデーション
- **オプティミスティックアップデート**: 送信前の即時UI反映
- **キーボード制御**: Enter送信、Shift+Enter改行対応

### MessageItem.tsx（メッセージ表示）

- **メッセージ色分け**: 自分/他人のメッセージを視覚的に区別
- **タイムスタンプ表示**: HH:mm形式での送信時刻表示
- **アニメーション**: 新着メッセージのフェードイン効果
- **テーマ連携**: Mantineダークモード対応

## 🔗 バックエンド連携

### REST API

| エンドポイント                        | メソッド | 説明               |
| ------------------------------------- | -------- | ------------------ |
| `/api/channels`                       | GET      | チャンネル一覧取得 |
| `/api/channels/{channel_id}/messages` | GET      | メッセージ履歴取得 |

### WebSocket通信

**エンドポイント:** `ws://localhost:8000/ws`

**データフロー:**

1. メッセージ送信 → ローカル状態即時更新
2. WebSocketでバックエンド送信
3. 保存確認レスポンス受信
4. エラー時のロールバック処理

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
- Props drilling最小限

## 🔍 開発コマンド

```bash
# プロダクションビルド
npm run build

# ビルド結果プレビュー
npm run preview

# ESLintチェック
npm run lint
```

> **Note:** 開発サーバー起動（`npm run dev`）については、上記の[クイックスタート](#-クイックスタート)をご参照ください。

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

## 🚧 今後の拡張予定

- [ ] ユーザー認証機能
- [ ] メッセージ検索
- [ ] ファイルアップロード
- [ ] 絵文字リアクション
- [ ] プッシュ通知
- [ ] タイピングインジケーター
