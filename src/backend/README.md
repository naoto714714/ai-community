# AI Community Backend

FastAPI + SQLAlchemy + WebSocketによるリアルタイムチャットアプリケーションのバックエンド

## 🚀 クイックスタート

```bash
# 依存関係インストール
uv sync

# 開発サーバー起動
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

バックエンドAPI: `http://localhost:8000`

## 📁 プロジェクト構造

```
src/backend/
├── main.py          # FastAPIアプリケーション
├── database.py      # データベース設定
├── models.py        # SQLAlchemyモデル
├── schemas.py       # Pydanticスキーマ
├── crud.py          # データベース操作
├── websocket.py     # WebSocket処理
├── pyproject.toml   # プロジェクト設定
└── chat.db          # SQLiteデータベース
```

## 🔧 技術スタック

- **Python**: 3.13
- **FastAPI**: Webフレームワーク
- **SQLAlchemy**: ORM
- **SQLite**: データベース
- **WebSocket**: リアルタイム通信
- **Pydantic**: データバリデーション
- **uvicorn**: ASGIサーバー

## 🗄️ データモデル

### Channel
- `id`: str (主キー)
- `name`: str (チャンネル名)
- `description`: str (説明)
- `created_at`: datetime

### Message
- `id`: str (主キー)
- `channel_id`: str (チャンネルID)
- `user_id`: str (ユーザーID)
- `user_name`: str (ユーザー名)
- `content`: str (メッセージ内容)
- `timestamp`: datetime (送信時刻)
- `is_own_message`: bool (自分のメッセージか)
- `created_at`: datetime (作成時刻)

## 🔗 API仕様

### REST API
- `GET /` - ヘルスチェック
- `GET /api/channels` - チャンネル一覧取得
- `GET /api/channels/{channel_id}/messages` - メッセージ履歴取得

### WebSocket
- `ws://localhost:8000/ws` - リアルタイム通信
  - メッセージ送信: `{"type": "message:send", "data": {...}}`
  - メッセージ保存通知: `{"type": "message:saved", "data": {...}}`

## 🔨 開発ルール

### パッケージ管理
- **必須**: `uv`のみ使用（`pip`は使用禁止）
- インストール: `uv add package`
- 開発依存: `uv add --dev package`

### コード品質
- 型ヒント必須
- パブリック関数にdocstring
- 行の長さ: 最大120文字
- 関数は小さく、単一責任

### テスト
- フレームワーク: `uv run --frozen pytest`
- 非同期テスト: anyio使用
- 新機能・バグ修正時は必ずテスト追加

## 🔍 開発コマンド

```bash
# フォーマット
uv run --frozen ruff format .

# リント
uv run --frozen ruff check .

# 型チェック
uv run --frozen pyright

# テスト
uv run --frozen pytest

# 開発サーバー起動
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 📋 実装済み機能

- ✅ FastAPI基本設定
- ✅ SQLAlchemy + SQLiteデータベース
- ✅ Channel/Messageモデル
- ✅ REST API（チャンネル一覧、メッセージ履歴）
- ✅ WebSocket通信
- ✅ リアルタイムメッセージ配信
- ✅ メッセージ永続化
- ✅ CORS設定
- ✅ エラーハンドリング