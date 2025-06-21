# AI Community Backend

FastAPI + SQLAlchemy + WebSocket + Google Gemini AI によるリアルタイムチャットアプリケーションのバックエンド

## 🚀 クイックスタート

```bash
# 依存関係インストール
uv sync

# 環境変数設定（AI機能使用時）
export GEMINI_API_KEY="あなたのGemini APIキー"

# 環境変数設定（Supabase使用時）
export SUPABASE_URL="あなたのSupabase URL"
export SUPABASE_KEY="あなたのSupabase APIキー"

# 開発サーバー起動
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**サーバーURL:** `http://localhost:8000`

## 📁 プロジェクト構造

```text
src/backend/
├── main.py              # FastAPIアプリケーション
├── database.py          # データベース設定
├── models.py            # SQLAlchemyモデル
├── schemas.py           # Pydanticスキーマ
├── crud.py              # データベース操作
├── ai/                  # AI機能
│   ├── gemini_client.py      # Gemini API クライアント
│   └── message_handlers.py   # AI応答処理
├── websocket/           # WebSocket処理
│   ├── handler.py       # WebSocketハンドラー
│   ├── manager.py       # 接続管理
│   └── types.py         # WebSocket型定義
├── utils/               # ユーティリティ
│   └── session_manager.py # セッション管理
└── chat.db              # SQLiteデータベース
```

## 🔧 技術スタック

- **Python:** 3.13
- **FastAPI:** Webフレームワーク
- **SQLAlchemy:** ORM
- **SQLite:** データベース
- **WebSocket:** リアルタイム通信
- **Pydantic:** データバリデーション
- **Google Gemini AI:** AI チャットボット
- **uvicorn:** ASGIサーバー

## 🗄️ データモデル

### Channel
```python
id: str              # 主キー
name: str            # チャンネル名
description: str     # 説明
created_at: datetime # 作成時刻
```

### Message
```python
id: str              # 主キー
channel_id: str      # チャンネルID
user_id: str         # ユーザーID（AI応答時は "ai_haruto"）
user_name: str       # ユーザー名（AI応答時は "ハルト"）
content: str         # メッセージ内容
timestamp: datetime  # 送信時刻
is_own_message: bool # 自分のメッセージか
created_at: datetime # 作成時刻
```

## 🤖 AI機能

### ハルト（AI チャットボット）

- **AI モデル**: Google Gemini 2.5 Flash Preview 05-20
- **トリガー**: メッセージに `@AI` を含める
- **人格**: 明るく親しみやすい関西弁混じりの男性
- **応答速度**: 平均2-3秒
- **プロンプト**: `prompts/001_ハルト.md` で設定
- **最適化**: チャット用途に最適化（思考機能を無効化して応答速度を重視）

#### Gemini 2.5 Flash の特徴
- **改良された推論能力**: 従来の1.5 Flashより高い品質の応答
- **思考機能**: デフォルトで有効だが、チャット用途では無効化（応答速度優先）
- **トークン効率**: 20-30%少ないトークン使用量で同等以上の品質を実現
- **1.0M トークンのコンテキストウィンドウ**: 長い会話履歴も処理可能

### AI応答フロー

1. ユーザーが `@AI` を含むメッセージを送信
2. WebSocketで受信・保存
3. Gemini APIで応答生成
4. AI応答をデータベースに保存
5. 全クライアントにブロードキャスト

## 🔗 API仕様

**Base URL**: `http://localhost:8000` (開発環境)

### 認証

現在は認証機能を実装していませんが、将来的に JWT トークンベースの認証を予定しています。

### エラーレスポンス

#### 標準エラーフォーマット

```json
{
  "detail": "エラーメッセージ"
}
```

#### HTTPステータスコード

- `200 OK`: 成功
- `400 Bad Request`: 無効なリクエスト
- `404 Not Found`: リソースが見つからない
- `422 Unprocessable Entity`: バリデーションエラー
- `500 Internal Server Error`: サーバーエラー

### REST API エンドポイント

#### GET /

**概要**: APIサーバーの動作確認

**レスポンス**:
```json
{
  "message": "AI Community Backend API"
}
```

#### GET /api/channels

**概要**: 全チャンネルの一覧を取得

**レスポンス**: `Array<ChannelResponse>`

```typescript
interface ChannelResponse {
  id: string;        // チャンネルID
  name: string;      // チャンネル名
  createdAt: string; // 作成日時 (ISO 8601)
}
```

#### GET /api/channels/{channel_id}/messages

**概要**: 指定チャンネルのメッセージ履歴を取得

**パラメータ**:

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|----|----|-----------|------|
| channel_id | string | ✅ | - | チャンネルID (パス) |
| limit | integer | ❌ | 100 | 取得件数上限 (1-1000) |
| offset | integer | ❌ | 0 | 取得開始位置 (0以上) |

**レスポンス**: `MessagesListResponse`

```typescript
interface MessagesListResponse {
  messages: MessageResponse[];
  total: number;    // 総メッセージ数
  hasMore: boolean; // さらにメッセージがあるか
}

interface MessageResponse {
  id: string;          // メッセージID
  channelId: string;   // チャンネルID
  userId: string;      // 送信者ID
  userName: string;    // 送信者名
  content: string;     // メッセージ本文
  timestamp: string;   // 送信時刻 (ISO 8601)
  isOwnMessage: boolean; // 送信者自身のメッセージか
  createdAt: string;   // 作成日時 (ISO 8601)
}
```

### WebSocket API

#### エンドポイント

`ws://localhost:8000/ws`

#### メッセージプロトコル

##### メッセージ送信

**リクエスト**:
```typescript
interface MessageSendRequest {
  type: "message:send";
  data: {
    id: string;          // 一意のメッセージID
    channel_id: string;  // 送信先チャンネルID
    user_id: string;     // 送信者ID
    user_name: string;   // 送信者名
    content: string;     // メッセージ本文
    timestamp: string;   // 送信時刻 (ISO 8601)
    is_own_message: boolean; // 送信者自身のメッセージか
  };
}
```

##### 成功レスポンス

```typescript
interface MessageSavedResponse {
  type: "message:saved";
  data: {
    id: string;      // 保存されたメッセージID
    success: true;
  };
}
```

##### エラーレスポンス

```typescript
interface MessageErrorResponse {
  type: "message:error";
  data: {
    id: string;      // エラーが発生したメッセージID
    success: false;
    error: string;   // エラーメッセージ
  };
}
```

##### AI応答ブロードキャスト

AI応答は自動的に全クライアントにブロードキャストされます：

```typescript
interface MessageBroadcastResponse {
  type: "message:broadcast";
  data: {
    id: string;
    channel_id: string;
    user_id: "ai_haruto";    // AI応答は固定
    user_name: "ハルト";     // AI応答は固定
    content: string;
    timestamp: string;
    is_own_message: false;   // AI応答は常にfalse
  };
}
```

## 🔨 開発ルール

### パッケージ管理
- **必須:** `uv`のみ使用（`pip`は使用禁止）
- インストール: `uv add package`
- 開発依存: `uv add --dev package`

### コード品質
- 型ヒント必須
- パブリック関数にdocstring
- 行の長さ: 最大120文字
- 関数は小さく、単一責任

### テスト
- フレームワーク: `pytest`
- 非同期テスト: `anyio`使用
- 新機能・バグ修正時は必ずテスト追加

## 🔍 開発コマンド

```bash
# コードフォーマット
uv run --frozen ruff format .

# リントチェック
uv run --frozen ruff check .

# 型チェック
uv run --frozen pyright

# テスト実行
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
- ✅ **Google Gemini AI統合**
- ✅ **AI チャットボット「ハルト」**
- ✅ **@AI メンション機能**
- ✅ 堅牢な接続管理システム
- ✅ セッション管理ユーティリティ
- ✅ CORS設定
- ✅ エラーハンドリング

## 🚧 今後の拡張予定

- [ ] ユーザー認証・セッション管理
- [ ] メッセージ検索API
- [ ] ファイルアップロード機能
- [ ] AI応答のカスタマイズ機能
- [ ] リアルタイム通知
- [ ] メッセージ暗号化
- [ ] レート制限機能

## 📊 パフォーマンス・制約

### 現在の制約

- **Message.content**: 最大長 2000文字
- **Message.id**: 一意（重複不可）
- **Channel.id**: 事前定義済みのみ有効（1-5）
- **timestamp**: ISO 8601 形式

### レート制限（予定）

- **WebSocket メッセージ**: 10件/分/接続
- **REST API**: 60リクエスト/分/IP
- **AI応答**: 3件/分/チャンネル

## 🛠️ 開発者向けツール

### API ドキュメント

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI JSON**: <http://localhost:8000/openapi.json>

### デバッグ用コマンド

```bash
# WebSocket接続テスト
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: test" -H "Sec-WebSocket-Version: 13" \
  http://localhost:8000/ws

# API動作確認
curl -v http://localhost:8000/api/channels
curl -v "http://localhost:8000/api/channels/1/messages?limit=10"
```
