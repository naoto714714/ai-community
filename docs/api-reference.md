# API リファレンス

## 概要

AI Community バックエンド API の詳細リファレンスです。
REST API と WebSocket API の両方について説明します。

**Base URL**: `http://localhost:8000` (開発環境)

## 認証

現在は認証機能を実装していませんが、将来的に JWT トークンベースの認証を予定しています。

## エラーレスポンス

### 標準エラーフォーマット

```json
{
  "detail": "エラーメッセージ"
}
```

### HTTPステータスコード

- `200 OK`: 成功
- `400 Bad Request`: 無効なリクエスト
- `404 Not Found`: リソースが見つからない
- `422 Unprocessable Entity`: バリデーションエラー
- `500 Internal Server Error`: サーバーエラー

## REST API エンドポイント

### GET /

**概要**: APIサーバーの動作確認

**レスポンス**:
```json
{
  "message": "AI Community Backend API"
}
```

**例**:
```bash
curl http://localhost:8000/
```

---

### GET /api/channels

**概要**: 全チャンネルの一覧を取得

**レスポンス**: `Array<ChannelResponse>`

**ChannelResponse**:
```typescript
interface ChannelResponse {
  id: string;        // チャンネルID
  name: string;      // チャンネル名
  createdAt: string; // 作成日時 (ISO 8601)
}
```

**レスポンス例**:
```json
[
  {
    "id": "1",
    "name": "雑談",
    "createdAt": "2024-01-01T00:00:00Z"
  },
  {
    "id": "2",
    "name": "ゲーム",
    "createdAt": "2024-01-01T00:00:00Z"
  }
]
```

**例**:
```bash
curl http://localhost:8000/api/channels
```

---

### GET /api/channels/{channel_id}/messages

**概要**: 指定チャンネルのメッセージ履歴を取得

**パラメータ**:

| パラメータ | 型 | 必須 | デフォルト | 説明 |
|-----------|----|----|-----------|------|
| channel_id | string | ✅ | - | チャンネルID (パス) |
| limit | integer | ❌ | 100 | 取得件数上限 (1-1000) |
| offset | integer | ❌ | 0 | 取得開始位置 (0以上) |

**レスポンス**: `MessagesListResponse`

**MessagesListResponse**:
```typescript
interface MessagesListResponse {
  messages: MessageResponse[];
  total: number;    // 総メッセージ数
  hasMore: boolean; // さらにメッセージがあるか
}
```

**MessageResponse**:
```typescript
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

**レスポンス例**:
```json
{
  "messages": [
    {
      "id": "msg_1704038400000",
      "channelId": "1",
      "userId": "user_123",
      "userName": "ユーザー",
      "content": "こんにちは！",
      "timestamp": "2024-01-01T12:00:00Z",
      "isOwnMessage": true,
      "createdAt": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "hasMore": false
}
```

**エラーレスポンス**:

`404 Not Found`: チャンネルが存在しない
```json
{
  "detail": "Channel not found"
}
```

**例**:
```bash
# 基本的な取得
curl "http://localhost:8000/api/channels/1/messages"

# ページネーション
curl "http://localhost:8000/api/channels/1/messages?limit=50&offset=100"
```

---

## WebSocket API

### エンドポイント

`ws://localhost:8000/ws`

### 接続

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('WebSocket connected');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onclose = () => {
  console.log('WebSocket disconnected');
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};
```

### メッセージプロトコル

#### メッセージ送信

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

**リクエスト例**:
```json
{
  "type": "message:send",
  "data": {
    "id": "msg_1704038400000",
    "channel_id": "1",
    "user_id": "user_123",
    "user_name": "ユーザー",
    "content": "WebSocketテストメッセージ",
    "timestamp": "2024-01-01T12:00:00Z",
    "is_own_message": true
  }
}
```

**JavaScript 送信例**:
```javascript
const message = {
  type: "message:send",
  data: {
    id: Date.now().toString(),
    channel_id: "1",
    user_id: "user_123",
    user_name: "ユーザー",
    content: "Hello WebSocket!",
    timestamp: new Date().toISOString(),
    is_own_message: true
  }
};

ws.send(JSON.stringify(message));
```

#### 成功レスポンス

```typescript
interface MessageSavedResponse {
  type: "message:saved";
  data: {
    id: string;      // 保存されたメッセージID
    success: true;
  };
}
```

**レスポンス例**:
```json
{
  "type": "message:saved",
  "data": {
    "id": "msg_1704038400000",
    "success": true
  }
}
```

#### エラーレスポンス

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

**レスポンス例**:
```json
{
  "type": "message:error",
  "data": {
    "id": "msg_1704038400000",
    "success": false,
    "error": "Invalid channel_id"
  }
}
```

### WebSocket エラー

#### 接続エラー

- **WebSocket protocol error**: 不正なプロトコル
- **Connection refused**: サーバーが応答しない
- **Invalid message format**: JSON形式エラー

#### 処理エラー

- **Unknown message type**: 未知のメッセージタイプ
- **Validation error**: データバリデーションエラー
- **Database error**: データベース操作エラー

## データ型定義

### TypeScript型定義

```typescript
// チャンネル
interface Channel {
  id: string;
  name: string;
}

interface ChannelResponse extends Channel {
  createdAt: string;
}

// メッセージ
interface Message {
  id: string;
  channelId: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: Date;
  isOwnMessage: boolean;
}

interface MessageCreate {
  id: string;
  channel_id: string;
  user_id: string;
  user_name: string;
  content: string;
  timestamp: string; // ISO 8601
  is_own_message: boolean;
}

interface MessageResponse {
  id: string;
  channelId: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: string; // ISO 8601
  isOwnMessage: boolean;
  createdAt: string; // ISO 8601
}

// ページネーション
interface MessagesListResponse {
  messages: MessageResponse[];
  total: number;
  hasMore: boolean;
}
```

### 制約

- **Message.content**: 最大長 2000文字
- **Message.id**: 一意（重複不可）
- **Channel.id**: 事前定義済みのみ有効（1-5）
- **timestamp**: ISO 8601 形式

## レート制限

現在は実装していませんが、将来的に以下の制限を予定:

- **WebSocket メッセージ**: 10件/分/接続
- **REST API**: 60リクエスト/分/IP
- **メッセージ長**: 2000文字まで

## バージョニング

- **現在のバージョン**: v0.1.0
- **APIバージョニング**: 今後 `/v1/` プレフィックスを追加予定
- **下位互換性**: メジャーバージョンアップ時まで保証

## 使用例

### 完全なチャットフロー

```javascript
// 1. WebSocket接続
const ws = new WebSocket('ws://localhost:8000/ws');

// 2. チャンネル一覧取得
const channels = await fetch('http://localhost:8000/api/channels')
  .then(res => res.json());

// 3. メッセージ履歴取得
const history = await fetch('http://localhost:8000/api/channels/1/messages')
  .then(res => res.json());

// 4. メッセージ送信
ws.onopen = () => {
  const message = {
    type: "message:send",
    data: {
      id: `msg_${Date.now()}`,
      channel_id: "1",
      user_id: "user_123",
      user_name: "ユーザー",
      content: "新しいメッセージ",
      timestamp: new Date().toISOString(),
      is_own_message: true
    }
  };

  ws.send(JSON.stringify(message));
};

// 5. 応答処理
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);

  if (data.type === 'message:saved') {
    console.log('メッセージが保存されました:', data.data.id);
  } else if (data.type === 'message:error') {
    console.error('エラー:', data.data.error);
  }
};
```

### エラーハンドリング例

```javascript
// REST API エラーハンドリング
async function getMessages(channelId) {
  try {
    const response = await fetch(`/api/channels/${channelId}/messages`);

    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('チャンネルが見つかりません');
      }
      throw new Error(`API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('メッセージ取得エラー:', error);
    throw error;
  }
}

// WebSocket エラーハンドリング
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  // 再接続ロジック
  setTimeout(() => {
    ws = new WebSocket('ws://localhost:8000/ws');
  }, 5000);
};
```

## 開発者向けツール

### API ドキュメント

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### デバッグ用ツール

```bash
# WebSocket接続テスト
cd src/backend
uv run python test_websocket.py

# API動作確認
curl -v http://localhost:8000/api/channels
```

### ログ確認

```bash
# バックエンドログ
tail -f app.log | grep -E "(WebSocket|ERROR)"
```

## 将来の拡張予定

### 認証API

```
POST /api/auth/login
POST /api/auth/logout
GET /api/auth/me
POST /api/auth/refresh
```

### ユーザー管理API

```
GET /api/users
GET /api/users/{user_id}
PUT /api/users/{user_id}
```

### ファイルアップロードAPI

```
POST /api/channels/{channel_id}/files
GET /api/files/{file_id}
```

### 検索API

```
GET /api/search/messages?q={query}&channel_id={channel_id}
```
