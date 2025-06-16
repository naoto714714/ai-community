# バックエンド

## 技術スタック

- **FastAPI** + **SQLAlchemy** + **SQLite**
- **WebSocket** (リアルタイム通信)  
- **Python 3.13** + **uv** (パッケージ管理)

## アーキテクチャ

```
main.py (FastAPI)
├── REST API (/api/*)
├── WebSocket (/ws)
├── models.py (SQLAlchemy)
├── schemas.py (Pydantic)
├── crud.py (DB操作)
└── chat.db (SQLite)
```

## 主要API

### REST API
- `GET /api/channels` - チャンネル一覧
- `GET /api/channels/{id}/messages` - メッセージ履歴

### WebSocket
- `ws://localhost:8000/ws`
- メッセージ送信: `{"type": "message:send", "data": {...}}`

## データモデル

```python
# Channel
{
  "id": "1",
  "name": "雑談"
}

# Message  
{
  "id": "msg_123",
  "channelId": "1", 
  "userId": "user",
  "userName": "ユーザー",
  "content": "メッセージ",
  "timestamp": "2024-01-01T12:00:00Z",
  "isOwnMessage": true
}
```

## 開発

```bash
cd src/backend
uv sync
uv run python main.py  # http://localhost:8000
```

## ツール

```bash
uv run --frozen ruff format .  # フォーマット
uv run --frozen ruff check .   # リント  
uv run --frozen pyright        # 型チェック
```