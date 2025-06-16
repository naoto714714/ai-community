# API リファレンス

**Base URL**: `http://localhost:8000`

## REST API

### GET /api/channels
チャンネル一覧を取得

**レスポンス**:
```json
[
  {"id": "1", "name": "雑談", "createdAt": "2024-01-01T00:00:00Z"}
]
```

### GET /api/channels/{channel_id}/messages
指定チャンネルのメッセージ履歴を取得

**パラメータ**:
- `limit`: 取得件数 (デフォルト: 100)
- `offset`: 取得開始位置 (デフォルト: 0)

**レスポンス**:
```json
{
  "messages": [
    {
      "id": "msg_123",
      "channelId": "1",
      "userId": "user",
      "userName": "ユーザー", 
      "content": "こんにちは",
      "timestamp": "2024-01-01T12:00:00Z",
      "isOwnMessage": true,
      "createdAt": "2024-01-01T12:00:00Z"
    }
  ],
  "total": 1,
  "hasMore": false
}
```

## WebSocket API

**エンドポイント**: `ws://localhost:8000/ws`

### メッセージ送信

**リクエスト**:
```json
{
  "type": "message:send",
  "data": {
    "id": "msg_123",
    "channel_id": "1",
    "user_id": "user",
    "user_name": "ユーザー",
    "content": "こんにちは",
    "timestamp": "2024-01-01T12:00:00Z",
    "is_own_message": true
  }
}
```

**成功レスポンス**:
```json
{
  "type": "message:saved",
  "data": {"id": "msg_123", "success": true}
}
```

**エラーレスポンス**:
```json
{
  "type": "message:error", 
  "data": {"id": "msg_123", "success": false, "error": "エラーメッセージ"}
}
```

## 自動生成ドキュメント

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc