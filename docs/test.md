# AI Community テストフレームワーク仕様書

## 概要

本ドキュメントは、AI Communityプロジェクトにおけるテストフレームワークの全体設計と実装方針を定義します。フロントエンドとバックエンドそれぞれのテスト戦略、ディレクトリ構成、および品質担保のための具体的な実装方法を記載しています。

## 現状の課題

現在、以下のような課題があります：
- バックエンドに雑なテストファイルが点在（test_websocket.py、test_comprehensive.py、run_step7_tests.py）
- フロントエンドのテストが未実装
- 統一されたテスト構成がない
- CI/CD統合の準備ができていない

## テスト全体方針

### 基本原則
1. **テスト駆動開発（TDD）**: 新機能開発時はテストファーストで実装
2. **継続的インテグレーション（CI）**: すべてのプルリクエストでテスト実行
3. **カバレッジ目標**: コード全体で80%以上、重要機能は100%

### テストレベル
1. **ユニットテスト**: 個々の関数・コンポーネントの動作確認
2. **統合テスト**: モジュール間連携の確認

## ディレクトリ構成

```
ai-community/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # pytest共通設定
│   ├── backend/                 # バックエンドテスト
│   │   ├── __init__.py
│   │   ├── conftest.py          # バックエンド固有のfixture
│   │   ├── unit/               # ユニットテスト
│   │   │   ├── __init__.py
│   │   │   ├── test_models.py
│   │   │   ├── test_schemas.py
│   │   │   ├── test_crud.py
│   │   │   └── test_websocket_handlers.py
│   │   └── integration/        # 統合テスト
│   │       ├── __init__.py
│   │       ├── test_api_channels.py
│   │       ├── test_api_messages.py
│   │       ├── test_websocket_flow.py
│   │       └── test_database_operations.py
│   └── frontend/               # フロントエンドテスト
│       ├── setup.ts            # Vitest設定
│       ├── utils/              # テストユーティリティ
│       │   ├── test-utils.tsx
│       │   ├── mocks.ts
│       │   └── websocket-mock.ts
│       ├── unit/               # ユニットテスト
│       │   ├── components/
│       │   │   ├── ChatMessage.test.tsx
│       │   │   ├── ChannelList.test.tsx
│       │   │   ├── MessageInput.test.tsx
│       │   │   └── MessageList.test.tsx
│       │   └── hooks/
│       │       └── useWebSocket.test.ts
│       └── integration/        # 統合テスト
│           ├── ChatApp.test.tsx
│           └── WebSocketConnection.test.tsx
```

## フロントエンドテスト

### 技術スタック
- **テストランナー**: Vitest
- **テストライブラリ**: React Testing Library
- **モック**: Mock Service Worker (MSW)
- **カバレッジ**: Vitest内蔵

### 実装詳細

#### 1. セットアップ（tests/frontend/setup.ts）
```typescript
import '@testing-library/jest-dom'
import { cleanup } from '@testing-library/react'
import { afterEach } from 'vitest'

// 各テスト後にクリーンアップ
afterEach(() => {
  cleanup()
})

// グローバルモック設定
vi.mock('nanoid', () => ({
  nanoid: () => 'test-id-12345'
}))
```

#### 2. テストユーティリティ（tests/frontend/utils/test-utils.tsx）
```typescript
import { render, RenderOptions } from '@testing-library/react'
import { MantineProvider } from '@mantine/core'
import { ReactElement } from 'react'

const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <MantineProvider>
      {children}
    </MantineProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }
```

#### 3. WebSocketモック（tests/frontend/utils/websocket-mock.ts）
```typescript
import { vi } from 'vitest'

export class MockWebSocket {
  url: string
  readyState: number = WebSocket.CONNECTING
  onopen: ((event: Event) => void) | null = null
  onclose: ((event: CloseEvent) => void) | null = null
  onmessage: ((event: MessageEvent) => void) | null = null
  onerror: ((event: Event) => void) | null = null

  constructor(url: string) {
    this.url = url
    setTimeout(() => {
      this.readyState = WebSocket.OPEN
      this.onopen?.(new Event('open'))
    }, 0)
  }

  send = vi.fn((data: string) => {
    // メッセージ送信のモック
  })

  close = vi.fn(() => {
    this.readyState = WebSocket.CLOSED
    this.onclose?.(new CloseEvent('close'))
  })

  // テスト用ヘルパー
  simulateMessage(data: any) {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify(data) }))
  }
}

// グローバルWebSocketのモック
global.WebSocket = MockWebSocket as any
```

#### 4. コンポーネントテスト例（tests/frontend/unit/components/ChatMessage.test.tsx）
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '../../utils/test-utils'
import { ChatMessage } from '@/components/ChatMessage'

describe('ChatMessage', () => {
  const mockMessage = {
    id: '1',
    content: 'Hello, World!',
    user_name: 'Test User',
    timestamp: '2025-01-16T10:00:00.000Z',
    is_own_message: false
  }

  it('メッセージを正しく表示する', () => {
    render(<ChatMessage message={mockMessage} />)
    
    expect(screen.getByText('Hello, World!')).toBeInTheDocument()
    expect(screen.getByText('Test User')).toBeInTheDocument()
  })

  it('自分のメッセージは右寄せで表示される', () => {
    const ownMessage = { ...mockMessage, is_own_message: true }
    render(<ChatMessage message={ownMessage} />)
    
    const messageElement = screen.getByText('Hello, World!').closest('div')
    expect(messageElement).toHaveStyle({ textAlign: 'right' })
  })

  it('タイムスタンプが正しくフォーマットされる', () => {
    render(<ChatMessage message={mockMessage} />)
    
    // dayjs形式で表示されることを確認
    expect(screen.getByText(/10:00/)).toBeInTheDocument()
  })
})
```

#### 5. 統合テスト例（tests/frontend/integration/ChatApp.test.tsx）
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '../utils/test-utils'
import { App } from '@/App'
import { MockWebSocket } from '../utils/websocket-mock'

describe('ChatApp Integration', () => {
  it('チャンネル切り替えでメッセージが更新される', async () => {
    render(<App />)
    
    // チャンネル一覧が表示される
    await waitFor(() => {
      expect(screen.getByText('雑談')).toBeInTheDocument()
      expect(screen.getByText('ゲーム')).toBeInTheDocument()
    })

    // ゲームチャンネルをクリック
    fireEvent.click(screen.getByText('ゲーム'))

    // APIリクエストが送信される
    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/channels/2/messages')
      )
    })
  })

  it('WebSocket経由でメッセージが送受信される', async () => {
    const mockWs = new MockWebSocket('ws://localhost:8000/ws')
    render(<App />)

    // 接続を待つ
    await waitFor(() => {
      expect(mockWs.readyState).toBe(WebSocket.OPEN)
    })

    // メッセージを入力して送信
    const input = screen.getByPlaceholderText('メッセージを入力...')
    fireEvent.change(input, { target: { value: 'Test message' } })
    fireEvent.submit(input.closest('form')!)

    // WebSocketでメッセージが送信される
    expect(mockWs.send).toHaveBeenCalledWith(
      expect.stringContaining('Test message')
    )

    // サーバーからのレスポンスをシミュレート
    mockWs.simulateMessage({
      type: 'message:broadcast',
      data: {
        id: 'msg-1',
        content: 'Test message',
        user_name: 'Test User',
        timestamp: new Date().toISOString()
      }
    })

    // メッセージが表示される
    await waitFor(() => {
      expect(screen.getByText('Test message')).toBeInTheDocument()
    })
  })
})
```


## バックエンドテスト

### 技術スタック
- **テストランナー**: pytest
- **非同期テスト**: pytest-asyncio
- **HTTPクライアント**: httpx
- **モック**: pytest-mock
- **カバレッジ**: pytest-cov

### 実装詳細

#### 1. 共通設定（tests/conftest.py）
```python
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.backend.main import app
from src.backend.database import Base, get_db
from src.backend.models import Channel

# テスト用データベース設定
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """セッション全体で使用するイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
def test_db():
    """テスト用のインメモリデータベース"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal()
    
    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()

@pytest.fixture
def client(test_db) -> TestClient:
    """同期テスト用クライアント"""
    return TestClient(app)

@pytest.fixture
async def async_client(test_db) -> AsyncGenerator[AsyncClient, None]:
    """非同期テスト用クライアント"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def seed_channels(test_db):
    """初期チャンネルデータの投入"""
    channels = [
        Channel(id=1, name="雑談", description="何でも話せる場所"),
        Channel(id=2, name="ゲーム", description="ゲームについて語ろう"),
        Channel(id=3, name="音楽", description="音楽の話題はこちら"),
        Channel(id=4, name="趣味", description="趣味の共有"),
        Channel(id=5, name="ニュース", description="最新情報をシェア"),
    ]
    
    test_db.add_all(channels)
    test_db.commit()
    
    return channels
```

#### 2. モデルテスト（tests/backend/unit/test_models.py）
```python
import pytest
from datetime import datetime
from src.backend.models import Channel, Message

def test_channel_creation(test_db):
    """チャンネルモデルの作成テスト"""
    channel = Channel(
        name="テストチャンネル",
        description="テスト用のチャンネル"
    )
    test_db.add(channel)
    test_db.commit()
    
    assert channel.id is not None
    assert channel.name == "テストチャンネル"
    assert channel.description == "テスト用のチャンネル"
    assert isinstance(channel.created_at, datetime)

def test_message_creation(test_db, seed_channels):
    """メッセージモデルの作成テスト"""
    channel = seed_channels[0]
    message = Message(
        channel_id=channel.id,
        user_id="test_user",
        user_name="テストユーザー",
        content="テストメッセージ"
    )
    test_db.add(message)
    test_db.commit()
    
    assert message.id is not None
    assert message.channel_id == channel.id
    assert message.user_id == "test_user"
    assert message.content == "テストメッセージ"
    assert isinstance(message.created_at, datetime)

def test_channel_messages_relationship(test_db, seed_channels):
    """チャンネルとメッセージのリレーションテスト"""
    channel = seed_channels[0]
    
    # 複数のメッセージを作成
    for i in range(3):
        message = Message(
            channel_id=channel.id,
            user_id=f"user_{i}",
            user_name=f"ユーザー{i}",
            content=f"メッセージ{i}"
        )
        test_db.add(message)
    
    test_db.commit()
    test_db.refresh(channel)
    
    assert len(channel.messages) == 3
    assert all(msg.channel_id == channel.id for msg in channel.messages)
```

#### 3. APIテスト（tests/backend/integration/test_api_channels.py）
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_get_channels(async_client: AsyncClient, seed_channels):
    """チャンネル一覧取得APIのテスト"""
    response = await async_client.get("/api/channels")
    
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 5
    assert data[0]["name"] == "雑談"
    assert all("id" in channel and "name" in channel for channel in data)

@pytest.mark.asyncio
async def test_get_channel_messages(async_client: AsyncClient, seed_channels, test_db):
    """チャンネルメッセージ取得APIのテスト"""
    from src.backend.models import Message
    
    # テストメッセージを作成
    channel = seed_channels[0]
    for i in range(15):
        message = Message(
            channel_id=channel.id,
            user_id=f"user_{i}",
            user_name=f"ユーザー{i}",
            content=f"テストメッセージ{i}"
        )
        test_db.add(message)
    test_db.commit()
    
    # ページネーションなし
    response = await async_client.get(f"/api/channels/{channel.id}/messages")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 15
    assert len(data["messages"]) == 15
    
    # ページネーションあり
    response = await async_client.get(
        f"/api/channels/{channel.id}/messages?limit=10&offset=5"
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["total"] == 15
    assert len(data["messages"]) == 10

@pytest.mark.asyncio
async def test_get_channel_messages_invalid_channel(async_client: AsyncClient):
    """存在しないチャンネルのメッセージ取得テスト"""
    response = await async_client.get("/api/channels/999/messages")
    
    assert response.status_code == 404
    assert response.json()["detail"] == "Channel not found"
```

#### 4. WebSocketテスト（tests/backend/integration/test_websocket_flow.py）
```python
import pytest
import json
from fastapi.testclient import TestClient
from src.backend.main import app

def test_websocket_connection(client: TestClient):
    """WebSocket接続の基本テスト"""
    with client.websocket_connect("/ws") as websocket:
        # 接続成功を確認
        data = websocket.receive_json()
        assert data["type"] == "connection:established"

def test_websocket_message_send(client: TestClient, seed_channels):
    """WebSocketメッセージ送信テスト"""
    with client.websocket_connect("/ws") as websocket:
        # 接続確認メッセージを受信
        websocket.receive_json()
        
        # メッセージを送信
        test_message = {
            "type": "message:send",
            "data": {
                "id": "test_msg_1",
                "channel_id": "1",
                "user_id": "test_user",
                "user_name": "テストユーザー",
                "content": "WebSocketテスト",
                "timestamp": "2025-01-16T10:00:00.000Z",
                "is_own_message": True
            }
        }
        
        websocket.send_json(test_message)
        
        # 保存確認メッセージを受信
        response = websocket.receive_json()
        assert response["type"] == "message:saved"
        assert response["data"]["success"] is True
        
        # ブロードキャストメッセージを受信
        broadcast = websocket.receive_json()
        assert broadcast["type"] == "message:broadcast"
        assert broadcast["data"]["content"] == "WebSocketテスト"

def test_websocket_invalid_message(client: TestClient):
    """無効なメッセージ送信テスト"""
    with client.websocket_connect("/ws") as websocket:
        # 接続確認メッセージを受信
        websocket.receive_json()
        
        # 無効なメッセージを送信（必須フィールドが不足）
        invalid_message = {
            "type": "message:send",
            "data": {
                "content": "不完全なメッセージ"
            }
        }
        
        websocket.send_json(invalid_message)
        
        # エラーレスポンスを確認
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "error" in response["data"]

@pytest.mark.asyncio
async def test_websocket_multiple_clients():
    """複数クライアント間のメッセージブロードキャストテスト"""
    client1 = TestClient(app)
    client2 = TestClient(app)
    
    with client1.websocket_connect("/ws") as ws1:
        with client2.websocket_connect("/ws") as ws2:
            # 両方のクライアントで接続確認
            ws1.receive_json()
            ws2.receive_json()
            
            # クライアント1からメッセージ送信
            message = {
                "type": "message:send",
                "data": {
                    "id": "broadcast_test",
                    "channel_id": "1",
                    "user_id": "user1",
                    "user_name": "ユーザー1",
                    "content": "ブロードキャストテスト",
                    "timestamp": "2025-01-16T10:00:00.000Z",
                    "is_own_message": True
                }
            }
            
            ws1.send_json(message)
            
            # クライアント1で保存確認とブロードキャストを受信
            ws1.receive_json()  # saved
            broadcast1 = ws1.receive_json()  # broadcast
            
            # クライアント2でブロードキャストを受信
            broadcast2 = ws2.receive_json()
            
            assert broadcast1["type"] == "message:broadcast"
            assert broadcast2["type"] == "message:broadcast"
            assert broadcast1["data"]["content"] == broadcast2["data"]["content"]
```


## テスト実行方法

### フロントエンドテスト

```bash
# フロントエンドディレクトリに移動
cd src/frontend

# 依存関係インストール（初回のみ）
npm install --save-dev vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event @playwright/test

# ユニットテスト・統合テスト実行
npm run test

# カバレッジ付きテスト実行
npm run test:coverage

# ウォッチモードでテスト実行
npm run test:watch
```

### バックエンドテスト

```bash
# プロジェクトルートディレクトリで実行
# 依存関係インストール（初回のみ）
uv add --dev pytest pytest-asyncio pytest-cov pytest-mock httpx

# 全テスト実行
uv run pytest

# カバレッジ付きテスト実行
uv run pytest --cov=src/backend --cov-report=html

# 特定のテストのみ実行
uv run pytest tests/backend/unit/
uv run pytest tests/backend/integration/

# 詳細出力付きテスト
uv run pytest -v

# 失敗したテストのみ再実行
uv run pytest --lf
```


## CI/CD統合

### GitHub Actions設定例（.github/workflows/test.yml）

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    
    - name: Install uv
      run: pip install uv
    
    - name: Install dependencies
      run: uv sync
    
    - name: Run backend tests
      run: uv run pytest tests/backend/ --cov=src/backend --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: backend

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      working-directory: ./src/frontend
      run: npm ci
    
    - name: Run frontend tests
      working-directory: ./src/frontend
      run: npm run test:coverage
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./src/frontend/coverage/lcov.info
        flags: frontend

```

## 既存テストファイルの整理

現在src/backend/に散在している以下のファイルは、新しいテスト構造に移行します：

1. **test_websocket.py** → `tests/backend/integration/test_websocket_flow.py`に統合
2. **test_comprehensive.py** → 各テストカテゴリに分割：
   - サーバー接続テスト → `tests/backend/integration/test_api_health.py`
   - チャンネルAPIテスト → `tests/backend/integration/test_api_channels.py`
   - WebSocketテスト → `tests/backend/integration/test_websocket_flow.py`
   - データベーステスト → `tests/backend/unit/test_database.py`
3. **run_step7_tests.py** → CI/CD統合に置き換え

移行手順：
1. 新しいテストディレクトリ構造を作成
2. 既存のテストコードを適切な場所に移動・リファクタリング
3. 古いテストファイルを削除
4. CI/CD設定を追加

## まとめ

このテストフレームワークにより、以下が実現されます：

1. **品質保証**: 包括的なテストカバレッジによる高品質なコード
2. **開発効率**: TDDによる迅速な開発サイクル
3. **保守性**: 明確なテスト構造による長期的な保守性
4. **信頼性**: CI/CDによる継続的な品質チェック
5. **ドキュメント**: テストコードがコードの仕様書として機能

定期的にテストカバレッジを確認し、重要な機能については100%のカバレッジを維持することで、プロジェクトの品質を担保します。