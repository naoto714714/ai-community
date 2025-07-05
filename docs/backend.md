# AI Community バックエンド仕様書

FastAPI、SQLAlchemy、WebSocket、Supabase PostgreSQL、Google Gemini AI を利用したリアルタイムチャットアプリケーションのバックエンド技術仕様書です。

## 1. アーキテクチャ概要

- **Webフレームワーク**: FastAPI
- **データベース**: Supabase PostgreSQL
- **ORM**: SQLAlchemy
- **リアルタイム通信**: WebSocket
- **AIチャットボット**: Google Gemini API
- **非同期サーバー**: Uvicorn

## 2. ディレクトリ構成

```text
src/backend/
├── main.py              # FastAPIアプリケーション
├── database.py          # データベース設定
├── models.py            # SQLAlchemyモデル
├── schemas.py           # Pydanticスキーマ
├── crud.py              # データベース操作
├── ai/                  # AI機能
│   ├── __init__.py              # AI機能パッケージ初期化
│   ├── gemini_client.py         # Gemini API クライアント
│   ├── message_handlers.py      # AI応答処理
│   ├── auto_conversation.py     # AI自律会話機能
│   ├── conversation_timer.py    # 自動会話タイマー管理
│   ├── conversation_config.py   # 自動会話設定管理
│   └── personality_manager.py   # AI人格管理
├── constants/           # 共通定数モジュール
│   ├── __init__.py      # パッケージ初期化
│   ├── ai_config.py     # AI機能関連定数
│   ├── logging.py       # ログ設定定数
│   └── timezone.py      # タイムゾーン定数
├── websocket/           # WebSocket処理
│   ├── handler.py       # WebSocketハンドラー
│   ├── manager.py       # 接続管理
│   └── types.py         # WebSocket型定義
├── utils/               # ユーティリティ
│   ├── session_manager.py # セッション管理
│   └── discord_webhook.py # Discord Webhook送信
└── alembic/             # データベースマイグレーション
    ├── env.py           # マイグレーション環境設定
    ├── script.py.mako   # マイグレーションスクリプトテンプレート
    └── versions/        # マイグレーションバージョン管理
```

## 3. API仕様

### 2.1. REST API

**Base URL**: `/`

#### エンドポイント

##### `GET /api/channels`

- **概要**: 全チャンネルの一覧を取得します。
- **成功レスポンス (200 OK)**: `application/json`
  ```json
  [
    {
      "id": "string",
      "name": "string",
      "createdAt": "string (ISO 8601)"
    }
  ]
  ```

##### `GET /api/channels/{channel_id}/messages`

- **概要**: 指定したチャンネルのメッセージ履歴を取得します。
- **パスパラメータ**:
  - `channel_id` (string, required): チャンネルID
- **クエリパラメータ**:
  - `limit` (integer, optional, default: 100): 取得件数 (1-1000)
  - `offset` (integer, optional, default: 0): 取得開始位置
- **成功レスポンス (200 OK)**: `application/json`
  ```json
  {
    "messages": [
      {
        "id": "string",
        "channelId": "string",
        "userId": "string",
        "userName": "string",
        "userType": "string (human or ai)",
        "content": "string",
        "timestamp": "string (ISO 8601)",
        "isOwnMessage": "boolean",
        "createdAt": "string (ISO 8601)"
      }
    ],
    "total": "integer",
    "hasMore": "boolean"
  }
  ```

### 2.2. WebSocket API

**エンドポイント**: `ws:///ws`

#### メッセージプロトコル

クライアントとサーバーはJSON形式のメッセージを送受信します。各メッセージは `type` と `data` プロパティを持ちます。

##### クライアント → サーバー

- **`message:send`**: メッセージを送信します。
  ```json
  {
    "type": "message:send",
    "data": {
      "id": "string",
      "channel_id": "string",
      "user_id": "string",
      "user_name": "string",
      "user_type": "string (user)",
      "content": "string",
      "timestamp": "string (ISO 8601)",
      "is_own_message": "boolean"
    }
  }
  ```

##### サーバー → クライアント

- **`message:saved`**: 送信されたメッセージが正常に保存されたことを通知します。
  ```json
  {
    "type": "message:saved",
    "data": {
      "id": "string",
      "success": true
    }
  }
  ```

- **`message:broadcast`**: 新しいメッセージ（ユーザーまたはAI）を全クライアントにブロードキャストします。
  ```json
  {
    "type": "message:broadcast",
    "data": {
      "id": "string",
      "channel_id": "string",
      "user_id": "string",
      "user_name": "string",
      "user_type": "string (human or ai)",
      "content": "string",
      "timestamp": "string (ISO 8601)",
      "is_own_message": false
    }
  }
  ```

- **`message:error`**: メッセージ処理中にエラーが発生したことを通知します。
  ```json
  {
    "type": "message:error",
    "data": {
      "id": "string",
      "success": false,
      "error": "string"
    }
  }
  ```

## 3. データモデル

SQLAlchemyで定義されたデータモデルです。

### `Channel`

| カラム名 | 型 | 説明 |
|---|---|---|
| `id` | `str` | 主キー |
| `name` | `str` | チャンネル名 |
| `description` | `str` | 説明 |
| `created_at` | `datetime` | 作成時刻 |

### `Message`

| カラム名 | 型 | 説明 |
|---|---|---|
| `id` | `str` | 主キー |
| `channel_id` | `str` | チャンネルID (FK) |
| `user_id` | `str` | ユーザーID |
| `user_name` | `str` | ユーザー名 |
| `user_type` | `str` | `user` または `ai` |
| `content` | `str` | メッセージ内容 |
| `timestamp` | `datetime` | 送信時刻 |
| `is_own_message`| `bool` | クライアントが自身のメッセージか判断するためのフラグ。APIレスポンスでは動的に設定されます。 |
| `created_at` | `datetime` | 作成時刻 |

## 4. AI機能

### 4.1. @AI メンション応答

- **トリガー**: メッセージ本文に `@AI` が含まれている場合。
- **動作**:
  1. `prompts/people/` からランダムにAI人格を選択。
  2. 過去10件のメッセージ履歴を文脈として取得。
  3. Gemini APIにプロンプトを送信し、応答を生成。
  4. 生成されたメッセージをDBに保存し、全クライアントにブロードキャスト。
- **特徴**:
  - **文脈理解**: 過去の会話の流れを汲んだ応答を生成します。
  - **人格の多様性**: 複数のAI人格がランダムに応答することで、会話の多様性を確保します。
  - **連続発言防止**: 同じAIが連続で応答しないように制御されます。

### 4.2. AI自律会話

- **概要**: 人間の介入なしに、AI同士が自動で会話を続ける機能。
- **トリガー**:
  - `AI_CONVERSATION_ENABLED=true` の場合、バックグラウンドでタイマーが作動。
  - `AI_CONVERSATION_TARGET_CHANNEL` で指定されたチャンネルが対象。
  - 最後のメッセージから `AI_CONVERSATION_INTERVAL_SECONDS` で指定された時間が経過した場合に発言。
- **動作**: `@AI` メンション応答と同様のフローで、AIが選択されメッセージを生成・投稿します。

### 4.3. Discord Webhook連携

- **概要**: AIの発言をリアルタイムで指定のDiscordチャンネルに転送します。
- **設定**: 環境変数 `DISCORD_WEBHOOK_URL` にWebhookのURLを設定することで有効になります。
- **機能**:
  - レート制限（30件/分）を考慮した送信制御。
  - メッセージ長の制限（2000文字）に対応。
  - Markdown特殊文字のエスケープ処理。

## 5. 開発者向け情報

### APIドキュメント

開発サーバー起動中、以下のURLでAPIドキュメントを確認できます。

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### 起動コマンド

```bash
# 開発サーバーをリロードモードで起動
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 --reload
```
