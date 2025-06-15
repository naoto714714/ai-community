# AI Community バックエンド実装手順書

## 概要

`simple-backend-spec.md`の仕様に基づいて、段階的にバックエンドを実装する手順書です。各ステップごとに動作確認しながら進めることで、確実に機能を構築できます。

---

## ステップ1: 環境セットアップとプロジェクト構造作成

### 1.1 プロジェクト構造の作成

```bash
# プロジェクトルートから実行
mkdir -p src/backend
cd src/backend

# 必要なファイルを作成
touch __init__.py
touch main.py
touch models.py
touch database.py
touch schemas.py
touch websocket.py
touch crud.py
```

### 1.2 uvでPython 3.13環境を確認

```bash
# Python 3.13が使用されているか確認
uv python --version

# Python 3.13でない場合は設定
uv python install 3.13
uv python pin 3.13
```

### 1.3 pyproject.tomlの作成（backendディレクトリ内）

```bash
# pyproject.tomlを作成
cat > pyproject.toml << 'EOF'
[project]
name = "ai-community-backend"
version = "0.1.0"
description = "Simple chat backend for AI Community"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0.25",
    "websockets>=12.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
EOF
```

### 1.4 依存関係のインストール

```bash
# 依存関係をインストール
uv sync
```

### 確認ポイント
- [ ] プロジェクト構造が正しく作成されている
- [ ] Python 3.13が使用されている
- [ ] 依存関係がインストールされている

---

## ステップ2: データベース設定とモデル定義

### 2.1 database.pyの実装

```python
# src/backend/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./chat.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
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

### 2.2 models.pyの実装

```python
# src/backend/models.py
from sqlalchemy import Column, String, Text, DateTime, Boolean
from datetime import datetime
from database import Base

class Channel(Base):
    __tablename__ = "channels"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    channel_id = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    is_own_message = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 2.3 schemas.pyの実装

```python
# src/backend/schemas.py
from pydantic import BaseModel
from datetime import datetime
from typing import List

class MessageBase(BaseModel):
    id: str
    channel_id: str
    user_id: str
    user_name: str
    content: str
    timestamp: datetime
    is_own_message: bool

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    created_at: datetime
    
    class Config:
        from_attributes = True

class ChannelBase(BaseModel):
    id: str
    name: str

class ChannelResponse(ChannelBase):
    created_at: datetime
    
    class Config:
        from_attributes = True

class MessagesListResponse(BaseModel):
    messages: List[MessageResponse]
    total: int
    has_more: bool
```

### 確認ポイント
- [ ] database.pyが正しく実装されている
- [ ] models.pyでデータベーステーブルが定義されている
- [ ] schemas.pyでPydanticモデルが定義されている

---

## ステップ3: 基本的なFastAPIアプリケーション作成

### 3.1 main.pyの基本実装

```python
# src/backend/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager
from typing import List

from database import SessionLocal, engine, get_db
from models import Base, Channel, Message
from schemas import ChannelResponse, MessageResponse, MessagesListResponse

# 初期チャンネルデータ
INITIAL_CHANNELS = [
    {"id": "1", "name": "雑談"},
    {"id": "2", "name": "ゲーム"},
    {"id": "3", "name": "音楽"},
    {"id": "4", "name": "趣味"},
    {"id": "5", "name": "ニュース"}
]

def init_channels():
    """初期チャンネルをデータベースに作成"""
    db = SessionLocal()
    try:
        for channel_data in INITIAL_CHANNELS:
            existing = db.query(Channel).filter(Channel.id == channel_data["id"]).first()
            if not existing:
                channel = Channel(**channel_data)
                db.add(channel)
        db.commit()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時処理
    Base.metadata.create_all(bind=engine)  # テーブル作成
    init_channels()  # 初期チャンネル作成
    yield
    # 終了時処理

app = FastAPI(
    title="AI Community Backend",
    description="Simple chat backend for AI Community",
    version="0.1.0",
    lifespan=lifespan
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "AI Community Backend API"}

@app.get("/api/channels", response_model=List[ChannelResponse])
async def get_channels(db: Session = Depends(get_db)):
    """チャンネル一覧取得"""
    channels = db.query(Channel).all()
    return channels

@app.get("/api/channels/{channel_id}/messages", response_model=MessagesListResponse)
async def get_channel_messages(
    channel_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """指定チャンネルのメッセージ履歴取得"""
    # チャンネルの存在確認
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # メッセージ取得
    messages = (
        db.query(Message)
        .filter(Message.channel_id == channel_id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    
    # 総数取得
    total = db.query(Message).filter(Message.channel_id == channel_id).count()
    has_more = (offset + limit) < total
    
    return MessagesListResponse(
        messages=messages,
        total=total,
        has_more=has_more
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

### 3.2 動作確認

```bash
# サーバー起動
cd src/backend
uv run python main.py
```

別のターミナルで動作確認:

```bash
# ルートエンドポイントのテスト
curl http://localhost:8000/

# チャンネル一覧取得
curl http://localhost:8000/api/channels

# メッセージ履歴取得（空の場合）
curl http://localhost:8000/api/channels/1/messages
```

### 確認ポイント
- [ ] サーバーが起動する
- [ ] ルートエンドポイントから応答がある
- [ ] チャンネル一覧が取得できる
- [ ] chat.dbファイルが作成されている

---

## ステップ4: CRUD操作の実装

### 4.1 crud.pyの実装

```python
# src/backend/crud.py
from sqlalchemy.orm import Session
from models import Message, Channel
from schemas import MessageCreate
from datetime import datetime

def create_message(db: Session, message: MessageCreate) -> Message:
    """メッセージを作成"""
    # タイムスタンプを文字列からdatetimeオブジェクトに変換
    if isinstance(message.timestamp, str):
        timestamp = datetime.fromisoformat(message.timestamp.replace('Z', '+00:00'))
    else:
        timestamp = message.timestamp
    
    db_message = Message(
        id=message.id,
        channel_id=message.channel_id,
        user_id=message.user_id,
        user_name=message.user_name,
        content=message.content,
        timestamp=timestamp,
        is_own_message=message.is_own_message
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def get_channel_messages(db: Session, channel_id: str, skip: int = 0, limit: int = 100):
    """チャンネルのメッセージを取得"""
    return (
        db.query(Message)
        .filter(Message.channel_id == channel_id)
        .order_by(Message.created_at.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )

def get_channels(db: Session):
    """全チャンネルを取得"""
    return db.query(Channel).all()
```

### 4.2 main.pyの更新（CRUD使用）

```python
# src/backend/main.py に以下を追加
import crud

# get_channel_messages関数を更新
@app.get("/api/channels/{channel_id}/messages", response_model=MessagesListResponse)
async def get_channel_messages(
    channel_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """指定チャンネルのメッセージ履歴取得"""
    # チャンネルの存在確認
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    # メッセージ取得
    messages = crud.get_channel_messages(db, channel_id, offset, limit)
    
    # 総数取得
    total = db.query(Message).filter(Message.channel_id == channel_id).count()
    has_more = (offset + limit) < total
    
    return MessagesListResponse(
        messages=messages,
        total=total,
        has_more=has_more
    )

# get_channels関数を更新
@app.get("/api/channels", response_model=List[ChannelResponse])
async def get_channels(db: Session = Depends(get_db)):
    """チャンネル一覧取得"""
    return crud.get_channels(db)
```

### 確認ポイント
- [ ] crud.pyが正しく実装されている
- [ ] main.pyでCRUD関数が使用されている
- [ ] API動作が変わらず正常に動作する

---

## ステップ5: WebSocket機能の実装

### 5.1 websocket.pyの実装

```python
# src/backend/websocket.py
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Dict, List
import json
import logging

from database import SessionLocal
from schemas import MessageCreate
import crud

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # 接続が切れている場合は削除
                self.disconnect(connection)

manager = ConnectionManager()

async def handle_websocket_message(websocket: WebSocket, data: dict):
    """WebSocketメッセージの処理"""
    message_type = data.get("type")
    message_data = data.get("data")
    
    if message_type == "message:send":
        # データベースにメッセージを保存
        db = SessionLocal()
        try:
            message_create = MessageCreate(**message_data)
            saved_message = crud.create_message(db, message_create)
            
            # 保存成功をクライアントに通知
            response = {
                "type": "message:saved",
                "data": {
                    "id": saved_message.id,
                    "success": True
                }
            }
            await manager.send_personal_message(json.dumps(response), websocket)
            
            logger.info(f"Message saved: {saved_message.id}")
            
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            
            # エラーをクライアントに通知
            error_response = {
                "type": "message:error",
                "data": {
                    "id": message_data.get("id"),
                    "success": False,
                    "error": str(e)
                }
            }
            await manager.send_personal_message(json.dumps(error_response), websocket)
        
        finally:
            db.close()
    
    else:
        logger.warning(f"Unknown message type: {message_type}")
```

### 5.2 main.pyにWebSocketエンドポイントを追加

```python
# src/backend/main.py に以下を追加
from fastapi import WebSocket, WebSocketDisconnect
from websocket import manager, handle_websocket_message
import json
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(websocket, message)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received: {data}")
            except Exception as e:
                logger.error(f"Error handling WebSocket message: {str(e)}")
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket connection closed")
```

### 5.3 WebSocketのテスト

WebSocketテスト用のスクリプトを作成:

```python
# src/backend/test_websocket.py
import asyncio
import websockets
import json
from datetime import datetime

async def test_websocket():
    uri = "ws://localhost:8000/ws"
    try:
        async with websockets.connect(uri) as websocket:
            # テストメッセージを送信
            test_message = {
                "type": "message:send",
                "data": {
                    "id": f"test_{int(datetime.now().timestamp())}",
                    "channel_id": "1",
                    "user_id": "user",
                    "user_name": "テストユーザー",
                    "content": "WebSocketテストメッセージ",
                    "timestamp": datetime.now().isoformat() + "Z",
                    "is_own_message": True
                }
            }
            
            await websocket.send(json.dumps(test_message))
            print(f"Sent: {test_message}")
            
            # レスポンスを受信
            response = await websocket.recv()
            print(f"Received: {response}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
```

テスト実行:

```bash
# 別のターミナルでテスト実行
cd src/backend
uv run python test_websocket.py

# メッセージが保存されたか確認
curl http://localhost:8000/api/channels/1/messages
```

### 確認ポイント
- [ ] WebSocketエンドポイントが動作する
- [ ] メッセージがデータベースに保存される
- [ ] 保存成功の応答が返る
- [ ] REST APIでメッセージが取得できる

---

## ステップ6: フロントエンドとの連携

### 6.1 フロントエンドのWebSocket接続コード

フロントエンドのLayoutコンポーネントを更新する必要があります：

```typescript
// src/frontend/src/components/Layout.tsx の更新部分
import { AppShell } from '@mantine/core';
import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import { ChannelList } from './ChannelList';
import { ChatArea } from './ChatArea';
import { initialChannels } from '../data/channels';
import type { Message } from '../types/chat';

export function Layout() {
  const [activeChannelId, setActiveChannelId] = useState(
    initialChannels.length > 0 ? initialChannels[0].id : '',
  );
  const [messages, setMessages] = useState<Message[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  const currentChannel = useMemo(
    () => initialChannels.find((ch) => ch.id === activeChannelId),
    [activeChannelId],
  );

  // WebSocket接続の初期化
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws');
    wsRef.current = ws;

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('WebSocket message received:', data);
      
      if (data.type === 'message:saved') {
        console.log('Message saved confirmation:', data.data);
      } else if (data.type === 'message:error') {
        console.error('Message save error:', data.data);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    return () => {
      ws.close();
    };
  }, []);

  // チャンネル変更時にメッセージ履歴を取得
  useEffect(() => {
    if (activeChannelId) {
      fetch(`http://localhost:8000/api/channels/${activeChannelId}/messages`)
        .then(res => res.json())
        .then(data => {
          console.log('Loaded messages:', data);
          setMessages(data.messages);
        })
        .catch(err => console.error('Error loading messages:', err));
    }
  }, [activeChannelId]);

  const handleSendMessage = useCallback(
    (content: string) => {
      const userMessage: Message = {
        id: Date.now().toString(),
        channelId: activeChannelId,
        userId: 'user',
        userName: 'ユーザー',
        content,
        timestamp: new Date(),
        isOwnMessage: true,
      };

      // ローカルステートを即座に更新
      setMessages((prev) => [...prev, userMessage]);

      // WebSocketでバックエンドに送信
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        const wsMessage = {
          type: 'message:send',
          data: {
            id: userMessage.id,
            channel_id: userMessage.channelId,
            user_id: userMessage.userId,
            user_name: userMessage.userName,
            content: userMessage.content,
            timestamp: userMessage.timestamp.toISOString(),
            is_own_message: userMessage.isOwnMessage,
          }
        };
        
        wsRef.current.send(JSON.stringify(wsMessage));
      }

      // 自動返信機能は削除（バックエンドに移行済み）
    },
    [activeChannelId],
  );

  // 以下は既存のコードと同じ
  return (
    <AppShell navbar={{ width: 280, breakpoint: 'sm' }} padding='md'>
      <AppShell.Navbar p='md'>
        <ChannelList
          channels={initialChannels}
          activeChannelId={activeChannelId}
          onChannelSelect={setActiveChannelId}
        />
      </AppShell.Navbar>

      <AppShell.Main>
        <ChatArea
          channelId={activeChannelId}
          currentChannel={currentChannel}
          messages={messages}
          onSendMessage={handleSendMessage}
        />
      </AppShell.Main>
    </AppShell>
  );
}
```

### 6.2 動作確認

1. バックエンドサーバーを起動:
```bash
cd src/backend
uv run python main.py
```

2. フロントエンドサーバーを起動:
```bash
cd src/frontend
npm run dev
```

3. ブラウザで動作確認:
- http://localhost:5173 にアクセス
- メッセージを送信
- ページをリロードしてメッセージが保存されているか確認

### 確認ポイント
- [ ] フロントエンドからWebSocket接続できる
- [ ] メッセージ送信が正常に動作する
- [ ] メッセージがデータベースに保存される
- [ ] ページリロード後もメッセージが残っている

---

## ステップ7: 最終確認とテスト

### 7.1 総合テスト

以下の機能が正常に動作することを確認:

1. **チャンネル一覧取得**
```bash
curl http://localhost:8000/api/channels
```

2. **メッセージ送信（WebSocket）**
```bash
cd src/backend
uv run python test_websocket.py
```

3. **メッセージ履歴取得**
```bash
curl http://localhost:8000/api/channels/1/messages
```

4. **フロントエンド統合テスト**
- ブラウザでメッセージ送信
- チャンネル切り替え
- ページリロード後のメッセージ永続化確認

### 7.2 ログの確認

バックエンドサーバーのログで以下を確認:
- WebSocket接続ログ
- メッセージ保存ログ
- エラーがないこと

### 7.3 データベースの確認

SQLiteデータベースの内容を確認:

```bash
# SQLiteデータベースの内容確認
cd src/backend
sqlite3 chat.db

# SQLiteプロンプトで実行
.tables
SELECT * FROM channels;
SELECT * FROM messages;
.quit
```

### 確認ポイント
- [ ] 全ての機能が正常に動作する
- [ ] エラーログがない
- [ ] データベースにデータが正しく保存されている
- [ ] フロントエンドとバックエンドが正常に連携している

---

## 完了！

全てのステップが完了すると、以下の機能を持つバックエンドシステムが完成します:

✅ **実装済み機能**
- SQLiteを使用したメッセージ永続化
- FastAPIによるREST API
- WebSocketによるリアルタイム通信
- チャンネル別メッセージ管理
- フロントエンドとの連携

**プロジェクト構造（完成版）:**
```
src/backend/
├── __init__.py
├── main.py              # FastAPIアプリケーション
├── models.py            # SQLAlchemyモデル
├── database.py          # データベース設定
├── schemas.py           # Pydanticスキーマ
├── websocket.py         # WebSocket処理
├── crud.py              # データベース操作
├── test_websocket.py    # WebSocketテスト
├── pyproject.toml       # プロジェクト設定
└── chat.db              # SQLiteデータベース
```

### 次のステップ候補

実装が完了したら、以下の機能拡張を検討できます:
- メッセージ検索機能
- メッセージ編集・削除
- ファイルアップロード
- 絵文字リアクション
- メッセージのエクスポート機能