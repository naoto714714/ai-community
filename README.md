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

### 2. バックエンドのセットアップ・起動

```bash
# バックエンドディレクトリに移動
cd src/backend

# 依存関係のインストール
uv sync

# 開発サーバーの起動
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

バックエンドAPI: `http://localhost:8000`

### 3. フロントエンドのセットアップ・起動（別ターミナル）

```bash
# フロントエンドディレクトリに移動
cd src/frontend

# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev
```

フロントエンド: `http://localhost:5173`

### 4. その他のコマンド

#### フロントエンド
```bash
npm run build      # ビルド
npm run preview    # プレビュー
npm run lint       # ESLintチェック
```

#### バックエンド
```bash
uv run --frozen ruff format .    # コードフォーマット
uv run --frozen ruff check .     # リントチェック
uv run --frozen pyright          # 型チェック
```

## 🎯 使用方法

1. バックエンドとフロントエンドを両方起動
2. ブラウザで `http://localhost:5173` にアクセス
3. 左側のチャンネル一覧から好きなチャンネルを選択
4. メッセージを入力して送信
5. メッセージはSQLiteデータベースに永続化されます

## ✨ 実装済み機能

### フロントエンド
- [x] レスポンシブなチャンネル一覧
- [x] リアルタイムメッセージ表示
- [x] メッセージ入力・送信
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
