# AI Community

**AI チャットボット「ハルト」搭載**のモダンなリアルタイムチャットアプリケーション。フロントエンド（React）とバックエンド（FastAPI）のフルスタック構成で実装されています。

## 📋 プロジェクト概要

このプロジェクトは、React + TypeScript + Mantineを使用したフロントエンドと、FastAPI + SQLAlchemy + WebSocketを使用したバックエンドで構成されるチャットアプリケーションです。
リアルタイム通信・メッセージの永続化・AI チャットボット機能を実現しています。

### 主要機能

- 複数チャンネルでのチャット機能
- リアルタイムメッセージ送受信（WebSocket）
- メッセージの永続化（SQLite）
- **🤖 AI チャットボット「ハルト」**（Google Gemini 1.5 Flash）
- **@AI メンションでの AI 応答機能**
- モバイル対応レスポンシブデザイン
- ダークモード対応

## 🛠 技術スタック

### フロントエンド
- **React**: 19.x
- **TypeScript**: 5.x
- **Mantine**: 8.x（UIコンポーネントライブラリ）
- **Mantine Hooks**: カスタムフック集
- **Tabler Icons**: アイコンライブラリ
- **Vite**: ビルドツール
- **dayjs**: 日付処理

### バックエンド
- **FastAPI**: Webフレームワーク
- **SQLAlchemy**: ORM
- **SQLite**: データベース
- **WebSocket**: リアルタイム通信
- **Pydantic**: データバリデーション
- **Google Gemini AI**: AI チャットボット
- **Python**: 3.13

### 開発環境
- **ESLint**: コード品質管理（フロントエンド）
- **Prettier**: コードフォーマット
- **Vitest**: テストフレームワーク（フロントエンド）
- **Ruff**: リンター・フォーマッター（バックエンド）
- **Pyright**: 型チェッカー（バックエンド）
- **pre-commit**: Gitフック管理
- **uv**: Pythonパッケージマネージャー

## 📁 プロジェクト構成

```
ai-community/
├── docs/                      # ドキュメント
│   ├── backend.md            # バックエンド仕様書・API リファレンス
│   ├── frontend.md           # フロントエンド開発ガイド
│   ├── test.md               # テストガイド
│   └── contributing.md       # コントリビューションガイド
├── prompts/                   # プロンプトテンプレート・開発ガイドライン
│   ├── 001_ハルト.md         # AI人格プロンプト
│   ├── backend-guideline.md  # バックエンド開発ガイドライン
│   ├── frontend-guideline.md # フロントエンド開発ガイドライン
│   ├── code_review_guide.md  # コードレビューガイド
│   └── reviewer_personality.md # レビュー人格設定
├── src/
│   ├── backend/              # バックエンド（FastAPI + SQLite + AI）
│   │   ├── main.py          # FastAPIアプリケーション
│   │   ├── models.py        # SQLAlchemyモデル
│   │   ├── database.py      # データベース設定
│   │   ├── schemas.py       # Pydanticスキーマ
│   │   ├── crud.py          # データベース操作
│   │   ├── ai/              # AI機能
│   │   │   ├── gemini_client.py      # Gemini API クライアント
│   │   │   └── message_handlers.py   # AI応答処理
│   │   ├── websocket/       # WebSocket処理
│   │   │   ├── handler.py   # WebSocketハンドラー
│   │   │   ├── manager.py   # 接続管理
│   │   │   └── types.py     # WebSocket型定義
│   │   ├── utils/           # ユーティリティ
│   │   │   └── session_manager.py # セッション管理
│   │   └── chat.db          # SQLiteデータベース
│   ├── frontend/            # フロントエンド（React + Mantine）
│   │   ├── src/
│   │   │   ├── App.tsx      # メインアプリケーション
│   │   │   ├── main.tsx     # エントリーポイント
│   │   │   ├── index.css    # グローバルスタイル
│   │   │   ├── components/  # Reactコンポーネント
│   │   │   │   ├── Layout.tsx       # アプリケーションレイアウト
│   │   │   │   ├── ChannelList.tsx  # チャンネル一覧
│   │   │   │   ├── ChatArea.tsx     # チャット画面
│   │   │   │   ├── MessageList.tsx  # メッセージ一覧
│   │   │   │   ├── MessageItem.tsx  # メッセージ表示
│   │   │   │   └── MessageInput.tsx # メッセージ入力
│   │   │   ├── types/       # TypeScript型定義
│   │   │   │   └── chat.ts  # Message, Channel型
│   │   │   └── data/        # 初期データ
│   │   │       └── channels.ts # 初期チャンネルデータ
│   │   ├── package.json     # フロントエンドNPM設定
│   │   ├── vite.config.ts   # Vite設定
│   │   └── tsconfig.json    # TypeScript設定
│   └── shared/              # 共有モジュール（空）
├── tests/                   # テスト
│   ├── backend/             # バックエンドテスト
│   │   ├── test_models.py   # モデルテスト
│   │   ├── test_api.py      # REST APIテスト
│   │   └── test_websocket.py # WebSocket + AI機能テスト
│   └── frontend/            # フロントエンドテスト
│       ├── components.test.tsx # コンポーネントテスト
│       └── integration.test.tsx # 統合テスト
├── z/                       # 一時ファイル・作業用
├── CLAUDE.md                # AI開発ガイドライン
├── package.json             # ルートNPM設定（並行実行用）
├── pyproject.toml          # Python設定・依存関係
└── README.md               # このファイル
```

## 🚀 セットアップ・起動方法

### 1. 前提条件

- Node.js 18.x以上
- Python 3.13以上
- npm
- uv (Python package manager)
- Google Gemini API キー（AI機能使用時、オプション）

### 2. 🎯 一発起動（推奨）

```bash
# ルートディレクトリで
npm install
npm run dev
```

これでフロントエンドとバックエンドが同時に起動します！
（バックエンドの依存関係は自動で`uv sync`が実行されます）

- **フロントエンド**: `http://localhost:5173`
- **バックエンド**: `http://localhost:8000`

### 3. 個別起動（従来の方法）

#### バックエンドのみ
```bash
npm run backend:only
# または
cd src/backend
uv sync
uv run python main.py
```
※ `npm run backend:only`は自動で`uv sync`を実行します

#### フロントエンドのみ
```bash
npm run frontend:only
# または
cd src/frontend
npm install
npm run dev
```

### 4. 便利なコマンド一覧

| コマンド | 説明 |
|---------|------|
| `npm run dev` | 🚀 フロントエンド + バックエンド同時起動 |
| `npm run backend:only` | バックエンドのみ起動 |
| `npm run frontend:only` | フロントエンドのみ起動 |

#### フロントエンド詳細コマンド
```bash
cd src/frontend
npm run build      # ビルド
npm run preview    # プレビュー
npm run lint       # ESLintチェック
```

#### バックエンド詳細コマンド
```bash
cd src/backend
uv run --frozen ruff format .    # コードフォーマット
uv run --frozen ruff check .     # リントチェック
uv run --frozen pyright          # 型チェック
```

## 🎯 使用方法

1. `npm run dev` でアプリケーションを起動
2. ブラウザで `http://localhost:5173` にアクセス
3. 左側のチャンネル一覧から好きなチャンネルを選択
4. メッセージを入力（**Shift+Enter**で送信、**Enter**で改行）
5. **🤖 AI機能**: メッセージに「@AI」を含めると、ハルトが応答します
6. メッセージはSQLiteデータベースに永続化されます

### AI機能の使用例
```
@AI こんにちは！
@AI プログラミングで困ってます
@AI 今日の天気はどう？
```

## ✨ 実装済み機能

### フロントエンド
- [x] レスポンシブなチャンネル一覧
- [x] リアルタイムメッセージ表示
- [x] メッセージ入力・送信（Shift+Enter送信、Enter改行）
- [x] WebSocket通信
- [x] ダークモード対応

### バックエンド
- [x] REST API（チャンネル一覧、メッセージ履歴）
- [x] WebSocketによるリアルタイム通信
- [x] SQLiteデータベースによるメッセージ永続化
- [x] **Google Gemini AI統合**
- [x] **AI チャットボット「ハルト」**
- [x] **@AI メンション機能**
- [x] 堅牢な接続管理システム
- [x] チャンネル別メッセージ管理
- [x] CORS対応

## 🚧 今後の拡張予定

- [ ] ユーザー認証機能
- [ ] メッセージ検索機能
- [ ] ファイルアップロード機能
- [ ] 絵文字リアクション機能
- [ ] AI応答のカスタマイズ機能
- [ ] プッシュ通知機能

## 📝 ドキュメント

- [バックエンド仕様書・API リファレンス](docs/backend.md)
- [フロントエンド開発ガイド](docs/frontend.md)
- [テストガイド](docs/test.md)
- [コントリビューションガイド](docs/contributing.md)
- [バックエンド開発ガイドライン](prompts/backend-guideline.md)
- [フロントエンド開発ガイドライン](prompts/frontend-guideline.md)

## 🔧 開発について

詳細な開発ガイドラインは [CLAUDE.md](CLAUDE.md) を参照してください。
