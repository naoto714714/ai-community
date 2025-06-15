# AI Community シンプルバックエンド仕様書

## 概要

ローカル環境でメッセージを永続化するための最小限のバックエンドシステム。認証機能なし、単一ユーザー利用を前提とした設計。

## 技術スタック

- **Python**: 3.13
- **フレームワーク**: FastAPI
- **データベース**: SQLite（ローカルファイル）
- **ORM**: SQLAlchemy 2.0
- **WebSocket**: FastAPI内蔵サポート
- **ASGIサーバー**: uvicorn

## プロジェクト構造

```
src/backend/
├── __init__.py
├── main.py              # FastAPIアプリケーションのエントリーポイント
├── models.py            # データベースモデル定義
├── database.py          # データベース接続設定
├── schemas.py           # Pydanticスキーマ
├── websocket.py         # WebSocket処理
├── crud.py              # データベース操作
└── chat.db              # SQLiteデータベースファイル（自動生成）
```

## データモデル

### メッセージテーブル（messages）

```python
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)  # フロントエンドから送られてくるID
    channel_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    is_own_message = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### チャンネルテーブル（channels）

```python
class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## API エンドポイント

### 1. WebSocket接続
```
ws://localhost:8000/ws
```

**WebSocketメッセージフォーマット:**

送信（クライアント → サーバー）:
```json
{
  "type": "message:send",
  "data": {
    "id": "1234567890",
    "channelId": "1",
    "userId": "user",
    "userName": "ユーザー",
    "content": "こんにちは",
    "timestamp": "2025-06-15T10:00:00Z",
    "isOwnMessage": true
  }
}
```

受信（サーバー → クライアント）:
```json
{
  "type": "message:saved",
  "data": {
    "id": "1234567890",
    "success": true
  }
}
```

### 2. REST API

#### GET /api/channels
チャンネル一覧取得

**レスポンス:**
```json
[
  {"id": "1", "name": "雑談"},
  {"id": "2", "name": "ゲーム"},
  {"id": "3", "name": "音楽"},
  {"id": "4", "name": "趣味"},
  {"id": "5", "name": "ニュース"}
]
```

#### GET /api/channels/{channel_id}/messages
指定チャンネルのメッセージ履歴取得

**クエリパラメータ:**
- `limit`: 取得件数（デフォルト: 100）
- `offset`: オフセット（デフォルト: 0）

**レスポンス:**
```json
{
  "messages": [
    {
      "id": "1234567890",
      "channelId": "1",
      "userId": "user",
      "userName": "ユーザー",
      "content": "こんにちは",
      "timestamp": "2025-06-15T10:00:00Z",
      "isOwnMessage": true
    }
  ],
  "total": 150,
  "hasMore": true
}
```

## 実装詳細

### 1. database.py
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./chat.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}  # SQLite用設定
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. main.py（基本構造）
```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import json

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時処理
    Base.metadata.create_all(bind=engine)  # テーブル作成
    init_channels()  # 初期チャンネル作成
    yield
    # 終了時処理

app = FastAPI(lifespan=lifespan)

# CORS設定（フロントエンド連携用）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            if message["type"] == "message:send":
                # メッセージを保存
                save_message(message["data"])
                
                # 保存完了を通知
                await websocket.send_json({
                    "type": "message:saved",
                    "data": {
                        "id": message["data"]["id"],
                        "success": True
                    }
                })
    except WebSocketDisconnect:
        pass
```

### 3. 初期データ設定
```python
def init_channels():
    """初期チャンネルをデータベースに作成"""
    db = SessionLocal()
    channels = [
        {"id": "1", "name": "雑談"},
        {"id": "2", "name": "ゲーム"},
        {"id": "3", "name": "音楽"},
        {"id": "4", "name": "趣味"},
        {"id": "5", "name": "ニュース"}
    ]
    
    for channel_data in channels:
        existing = db.query(Channel).filter(Channel.id == channel_data["id"]).first()
        if not existing:
            channel = Channel(**channel_data)
            db.add(channel)
    
    db.commit()
    db.close()
```

## フロントエンドとの連携

### 1. WebSocket接続の変更
現在の自動返信機能を、バックエンドへの保存に変更:

```typescript
// フロントエンド側の変更例
const ws = new WebSocket('ws://localhost:8000/ws');

const handleSendMessage = (content: string) => {
  const message = {
    type: 'message:send',
    data: {
      id: Date.now().toString(),
      channelId: activeChannelId,
      userId: 'user',
      userName: 'ユーザー',
      content,
      timestamp: new Date().toISOString(),
      isOwnMessage: true
    }
  };
  
  // WebSocketで送信
  ws.send(JSON.stringify(message));
  
  // ローカルステートも更新
  setMessages(prev => [...prev, message.data]);
};
```

### 2. メッセージ履歴の取得
アプリ起動時やチャンネル切り替え時に履歴を取得:

```typescript
useEffect(() => {
  // チャンネル切り替え時にメッセージ履歴を取得
  fetch(`http://localhost:8000/api/channels/${channelId}/messages`)
    .then(res => res.json())
    .then(data => setMessages(data.messages));
}, [channelId]);
```

## 起動方法

```bash
# backendディレクトリに移動
cd src/backend

# 依存関係インストール
uv add fastapi sqlalchemy uvicorn websockets

# サーバー起動
uv run uvicorn main:app --reload --port 8000
```

## 開発時の注意点

1. **データベースファイル**: `chat.db`は自動生成されるため、gitignoreに追加
2. **ポート競合**: FastAPI(8000)とVite(5173)で異なるポートを使用
3. **CORS設定**: ローカル開発用に`http://localhost:5173`を許可
4. **タイムゾーン**: UTCで統一（フロントエンドで表示時に変換）

## テスト方法

### WebSocket接続テスト
```python
# test_websocket.py
import asyncio
import websockets
import json

async def test():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        message = {
            "type": "message:send",
            "data": {
                "id": "test123",
                "channelId": "1",
                "userId": "user",
                "userName": "テストユーザー",
                "content": "テストメッセージ",
                "timestamp": "2025-06-15T10:00:00Z",
                "isOwnMessage": True
            }
        }
        await websocket.send(json.dumps(message))
        response = await websocket.recv()
        print(f"Response: {response}")

asyncio.run(test())
```

### REST APIテスト
```bash
# チャンネル一覧取得
curl http://localhost:8000/api/channels

# メッセージ履歴取得
curl http://localhost:8000/api/channels/1/messages?limit=10
```

## 今後の拡張候補

1. **メッセージ編集・削除**: PUT/DELETE エンドポイント追加
2. **検索機能**: フルテキスト検索の実装
3. **ファイルアップロード**: 画像・ファイル送信対応
4. **メッセージのリアクション**: 絵文字リアクション機能
5. **メッセージのエクスポート**: CSV/JSON形式でのエクスポート