# AI Community

モダンでカジュアルなデザインのリアルタイムチャットアプリケーション。フロントエンド（React）とバックエンド（FastAPI）のフルスタック構成で実装されています。

## 📋 プロジェクト概要

このプロジェクトは、React + TypeScript + Mantineを使用したフロントエンドと、FastAPI + SQLAlchemy + WebSocketを使用したバックエンドで構成されるチャットアプリケーションです。
リアルタイム通信とメッセージの永続化を実現しています。

### 主要機能

- 複数チャンネルでのチャット機能
- リアルタイムメッセージ送受信（WebSocket）
- メッセージの永続化（SQLite）
- レスポンシブデザイン（PC版優先）
- ダークモード対応

## 🛠 技術スタック

### フロントエンド
- **React**: 18.x
- **TypeScript**: 5.x
- **Mantine**: 7.x（UIコンポーネントライブラリ）
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
- **Python**: 3.13

### 開発環境
- **ESLint**: コード品質管理（フロントエンド）
- **Prettier**: コードフォーマット
- **Ruff**: リンター・フォーマッター（バックエンド）
- **Pyright**: 型チェッカー（バックエンド）
- **pre-commit**: Gitフック管理
- **uv**: Pythonパッケージマネージャー

## 📁 プロジェクト構成

```
ai-community/
├── docs/                      # ドキュメント
│   ├── chat-app-spec.md      # フロントエンド仕様書
│   ├── backend-implementation-guide.md  # バックエンド実装手順書
│   ├── simple-backend-spec.md           # バックエンド仕様書
│   ├── frontend-guideline.md           # フロントエンド開発ガイドライン
│   └── backend-guideline.md            # バックエンド開発ガイドライン
├── src/
│   ├── backend/              # バックエンド（FastAPI + SQLite）
│   │   ├── main.py          # FastAPIアプリケーション
│   │   ├── models.py        # SQLAlchemyモデル
│   │   ├── database.py      # データベース設定
│   │   ├── schemas.py       # Pydanticスキーマ
│   │   ├── websocket.py     # WebSocket処理
│   │   ├── crud.py          # データベース操作
│   │   └── chat.db          # SQLiteデータベース
│   └── frontend/            # フロントエンド（React + Mantine）
│       ├── src/
│       │   ├── components/  # Reactコンポーネント
│       │   ├── types/       # TypeScript型定義
│       │   └── data/        # 初期データ
│       └── package.json     # NPM設定
├── CLAUDE.md                # AI開発ガイドライン
├── .gitignore              # Git除外設定
├── .pre-commit-config.yaml # pre-commit設定
├── pyproject.toml          # Python設定
└── README.md               # このファイル
```

## 🚀 セットアップ・起動方法

### 1. 前提条件

- Node.js 18.x以上
- Python 3.13以上
- npm
- uv (Python package manager)

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
5. メッセージはSQLiteデータベースに永続化されます

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
- [x] チャンネル別メッセージ管理
- [x] CORS対応

## 🚧 今後の拡張予定

- [ ] ユーザー認証機能
- [ ] メッセージ検索機能
- [ ] ファイルアップロード機能
- [ ] 絵文字リアクション機能
- [ ] スマートフォン対応

## 📝 ドキュメント

- [フロントエンド仕様書](docs/chat-app-spec.md)
- [バックエンド実装手順書](docs/backend-implementation-guide.md)
- [バックエンド仕様書](docs/simple-backend-spec.md)
- [フロントエンド開発ガイドライン](docs/frontend-guideline.md)
- [バックエンド開発ガイドライン](docs/backend-guideline.md)

## 🔧 開発について

詳細な開発ガイドラインは [CLAUDE.md](CLAUDE.md) を参照してください。
