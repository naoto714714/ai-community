# AI Community テストガイド

## 概要

AI Community プロジェクトの**実用的でメンテナンス可能な**テストガイドです。
Google Gemini AI統合チャットアプリケーションの品質を確保しつつ、開発効率を重視したテスト設計を採用しています。

## 基本方針

### 現実的な目標
- **品質 > 完璧性**: 重要機能の確実な動作を優先
- **保守性 > 網羅性**: メンテナンスしやすいテストを重視
- **段階的導入**: 必要最小限から始めて徐々に拡張
- **AI機能対応**: Google Gemini統合によるチャットボット「ハルト」の応答品質とWebSocket通信の安定性を確保

### テストレベル

1. **コアテスト**: 最重要機能のテスト（必須）

2. **AI機能テスト**: チャットボット・WebSocket通信テスト（推奨）

3. **拡張テスト**: 追加機能のテスト（任意）

## 簡素なディレクトリ構成

```text
ai-community/
├── tests/
│   ├── conftest.py              # pytest設定
│   ├── backend/                 # バックエンドテスト（5ファイル）
│   │   ├── conftest.py         # バックエンド専用設定
│   │   ├── test_models.py      # モデルテスト
│   │   ├── test_api.py         # REST API テスト
│   │   ├── test_websocket.py   # WebSocket + AI機能テスト
│   │   └── test_supabase_integration.py # Supabase統合テスト
│   └── frontend/               # フロントエンドテスト（3ファイル）
│       ├── setup.ts            # Vitest設定
│       ├── components.test.tsx  # コンポーネントテスト
│       └── integration.test.tsx # 統合テスト（AI応答含む）
├── src/
│   ├── backend/                # バックエンドソースコード
│   │   ├── main.py            # FastAPIアプリケーション
│   │   ├── models.py          # SQLAlchemyモデル
│   │   └── ...                # その他のバックエンドファイル
│   └── frontend/              # フロントエンドソースコード
│       ├── vitest.config.ts   # Vitestメイン設定
│       └── package.json       # テストスクリプト定義
└── pyproject.toml              # Pythonテスト設定
```

**総テスト数目標**: 約25個（バックエンド17個 + フロントエンド8個）

## バックエンドテスト（Python + pytest）

### 1. test_models.py（3テスト）
```python
from datetime import datetime
from models import Channel, Message

def test_channel_creation(test_db):
    """チャンネルモデルの作成テスト"""
    # チャンネル作成
    channel = Channel(id="test_1", name="テストチャンネル", description="テスト用")
    test_db.add(channel)
    test_db.commit()
    
    # 作成されたチャンネルの確認
    saved_channel = test_db.query(Channel).filter(Channel.id == "test_1").first()
    assert saved_channel is not None
    assert saved_channel.name == "テストチャンネル"
    assert saved_channel.description == "テスト用"

def test_message_creation(test_db, seed_channels):
    """メッセージモデルの作成テスト"""
    
    # メッセージ作成
    message = Message(
        id="msg_test_1",
        channel_id="1",
        user_id="user_123",
        user_name="テストユーザー",
        content="テストメッセージ",
        timestamp=datetime.now(),
        is_own_message=True
    )
    test_db.add(message)
    test_db.commit()
    
    # 作成されたメッセージの確認
    saved_message = test_db.query(Message).filter(Message.id == "msg_test_1").first()
    assert saved_message is not None
    assert saved_message.content == "テストメッセージ"
    assert saved_message.user_name == "テストユーザー"

def test_message_channel_relationship(test_db, seed_channels):
    """チャンネル-メッセージ関係テスト"""
    # チャンネルにメッセージを追加
    message = Message(
        id="msg_rel_1",
        channel_id="1",
        user_id="user_456",
        user_name="関係テストユーザー",
        content="関係テストメッセージ",
        timestamp=datetime.now(),
        is_own_message=False
    )
    test_db.add(message)
    test_db.commit()
    
    # チャンネルからメッセージを取得
    channel = test_db.query(Channel).filter(Channel.id == "1").first()
    messages = test_db.query(Message).filter(Message.channel_id == channel.id).all()
    
    assert len(messages) >= 1
    assert any(msg.id == "msg_rel_1" for msg in messages)
```

### 2. test_api.py（4テスト）
```python
async def test_get_channels(test_client):
    """チャンネル一覧取得 API テスト"""
    response = test_client.get("/api/channels")
    assert response.status_code == 200
    channels = response.json()
    assert isinstance(channels, list)
    assert len(channels) > 0
    assert "id" in channels[0]
    assert "name" in channels[0]

async def test_get_messages(test_client, seed_data):
    """メッセージ履歴取得 API テスト"""
    response = test_client.get("/api/channels/1/messages")
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    assert "total" in data
    assert "hasMore" in data
    assert isinstance(data["messages"], list)

async def test_get_messages_with_pagination(test_client, seed_data):
    """ページネーション付きメッセージ取得テスト"""
    response = test_client.get("/api/channels/1/messages?limit=5&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) <= 5
    assert data["total"] >= 0
    assert isinstance(data["hasMore"], bool)

async def test_invalid_channel(test_client):
    """存在しないチャンネルのエラーハンドリングテスト"""
    response = test_client.get("/api/channels/999/messages")
    assert response.status_code == 404
    error_data = response.json()
    assert "detail" in error_data
```

### 3. test_websocket.py（3テスト）
```python
async def test_websocket_connection(test_client):
    """WebSocket接続テスト"""
    # WebSocket接続の基本テスト
    with test_client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        assert data is not None

async def test_websocket_message_send(test_client):
    """WebSocketメッセージ送信テスト"""
    # WebSocketでのメッセージ送信テスト
    with test_client.websocket_connect("/ws") as websocket:
        test_message = {
            "type": "message:send",
            "data": {
                "id": "test_msg_1",
                "channel_id": "1",
                "user_id": "test_user",
                "user_name": "テストユーザー",
                "content": "テストメッセージ",
                "timestamp": "2024-01-01T12:00:00Z",
                "is_own_message": True
            }
        }
        websocket.send_json(test_message)
        response = websocket.receive_json()
        assert response["type"] == "message:saved"

async def test_ai_response_trigger(test_client):
    """@AI メンション機能テスト（モック使用）"""
    # AI応答トリガーのテスト（モック使用）
    with test_client.websocket_connect("/ws") as websocket:
        ai_message = {
            "type": "message:send",
            "data": {
                "id": "ai_test_msg_1",
                "channel_id": "1", 
                "user_id": "test_user",
                "user_name": "テストユーザー",
                "content": "@AI テストしています",
                "timestamp": "2024-01-01T12:00:00Z",
                "is_own_message": True
            }
        }
        websocket.send_json(ai_message)
        # AI応答をモックして確認
        response = websocket.receive_json()
        assert response["type"] in ["message:saved", "message:broadcast"]
```

## フロントエンドテスト（TypeScript + Vitest + Testing Library）

### 1. components.test.tsx（5テスト）
```typescript
// 主要コンポーネントのユニットテスト
describe('MessageItem', () => {
  it('通常メッセージが正しく表示される', () => {
    const message = { content: "テストメッセージ", userName: "ユーザー" };
    render(<MessageItem message={message} />);
    expect(screen.getByText("テストメッセージ")).toBeInTheDocument();
  });
  
  it('自分のメッセージは適切なスタイルで表示される', () => {
    const ownMessage = { content: "自分のメッセージ", isOwnMessage: true };
    render(<MessageItem message={ownMessage} />);
    expect(screen.getByTestId('own-message')).toHaveClass('own-message-style');
  });
  
  it('AI応答メッセージ（ハルト）が正しく表示される', () => {
    const aiMessage = { content: "こんにちは！", userName: "ハルト" };
    render(<MessageItem message={aiMessage} />);
    expect(screen.getByText("ハルト")).toBeInTheDocument();
    expect(screen.getByTestId('ai-message')).toBeInTheDocument();
  });
});

describe('MessageInput', () => {
  it('テキスト入力が正常に動作する', async () => {
    render(<MessageInput onSendMessage={vi.fn()} />);
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'テストメッセージ');
    expect(input).toHaveValue('テストメッセージ');
  });
  
  it('Shift+Enterでメッセージが送信される', async () => {
    const onSendMessage = vi.fn();
    render(<MessageInput onSendMessage={onSendMessage} />);
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'メッセージ送信テスト');
    await userEvent.keyboard('{Shift>}{Enter}{/Shift}');
    expect(onSendMessage).toHaveBeenCalledWith('メッセージ送信テスト');
  });
});
```

### 2. integration.test.tsx（3テスト）
```typescript
describe('ChatApp Integration', () => {
  it('チャンネル切り替えでメッセージが更新される', async () => {
    render(<ChatApp />);
    
    // 最初のチャンネルを選択
    await userEvent.click(screen.getByText('雑談'));
    expect(screen.getByTestId('channel-1-messages')).toBeInTheDocument();
    
    // 別のチャンネルに切り替え
    await userEvent.click(screen.getByText('ゲーム'));
    expect(screen.getByTestId('channel-2-messages')).toBeInTheDocument();
  });
  
  it('WebSocket経由でメッセージが送受信される', async () => {
    // WebSocketモック設定
    const mockWebSocket = vi.fn();
    global.WebSocket = mockWebSocket;
    
    render(<ChatApp />);
    const input = screen.getByRole('textbox');
    await userEvent.type(input, 'WebSocketテスト');
    await userEvent.keyboard('{Shift>}{Enter}{/Shift}');
    
    expect(mockWebSocket).toHaveBeenCalled();
  });
  
  it('@AI メンション付きメッセージの送信とAI応答の受信', async () => {
    render(<ChatApp />);
    const input = screen.getByRole('textbox');
    
    await userEvent.type(input, '@AI こんにちは');
    await userEvent.keyboard('{Shift>}{Enter}{/Shift}');
    
    // AI応答の表示を確認
    await waitFor(() => {
      expect(screen.getByText(/ハルト/)).toBeInTheDocument();
    });
  });
});
```

## テスト技術スタック

### バックエンド（Python 3.13）
- **pytest**: テストランナー・フィクスチャ管理
- **pytest-asyncio**: 非同期テスト対応
- **httpx**: 非同期HTTPクライアント（FastAPI テスト用）
- **pytest-mock**: モック機能（AI応答テスト用）
- **SQLite**: インメモリテスト用データベース（テスト専用）
- **Supabase PostgreSQL**: 本番データベース（統合テスト時）
- **anyio**: 非同期フレームワーク（uvと互換）

### フロントエンド（React 19 + TypeScript）
- **Vitest**: 高速テストランナー（Jest互換）
- **@testing-library/react**: Reactコンポーネントテスト
- **@testing-library/user-event**: ユーザーインタラクションテスト
- **@testing-library/jest-dom**: DOM assertion拡張
- **jsdom**: ブラウザ環境シミュレーション
- **msw**: WebSocket・API モック

## 実装状況・優先順位

### ✅ Phase 1: コアテスト（完了済み）
- [x] バックエンドモデルテスト（3個）
- [x] バックエンドAPIテスト（4個）
- [x] フロントエンドコンポーネントテスト（5個）

### ✅ Phase 2: 統合・AI機能テスト（完了済み）
- [x] WebSocket通信テスト（3個）
- [x] フロントエンド統合テスト（3個）
- [x] AI応答機能テスト（モック使用）

### ✅ Phase 3: Supabase統合テスト（完了済み）
- [x] Supabase接続確認テスト（2個）
- [x] PostgreSQL CRUD操作テスト（2個、環境依存でスキップ可）
- [x] データベースフォールバック機能テスト（3個）

#### 実行環境別の注意事項
- **ローカル開発**: 環境変数未設定時は自動スキップ
- **CI/CD環境**: Supabase接続情報をSecrets管理
- **セキュリティ**: 本番DBへの直接テスト実行は禁止
- **テストデータ**: テスト専用Supabaseプロジェクトを推奨

### 🚧 Phase 4: 拡張テスト（任意・将来予定）
- [ ] エラーハンドリング詳細テスト
- [ ] AI応答パフォーマンステスト
- [ ] E2Eテスト（Playwright使用予定）
- [ ] リアルタイム通信負荷テスト

## テスト実行方法

### バックエンドテスト
```bash
# 全テスト実行
cd src/backend && uv run --frozen pytest

# 特定テストファイル実行
uv run --frozen pytest tests/backend/test_models.py

# カバレッジ付き実行
uv run --frozen pytest --cov=src/backend
```

### フロントエンドテスト
```bash
# 全テスト実行
cd src/frontend && npm run test:run

# ウォッチモード
npm run test:dev

# カバレッジ付き実行
npm run test:coverage

# テストUI（ブラウザ表示）
npm run test:ui
```

## 品質指標・カバレッジ目標

- **現在達成**: 25テスト実装済み（既存18個 + Supabase統合7個）
- **カバレッジ目標**: 主要機能70%以上
- **AI機能テスト**: モック使用で基本動作確認済み
- **Supabase統合**: 接続・CRUD・フォールバック機能をテスト
- **継続的統合**: pre-commitフックでテスト自動実行

## まとめ

**理念**: 「実用性重視の品質確保」
- 25個の戦略的テストで主要機能の品質を確保
- AI機能・Supabase統合も含めた包括的なテストカバレッジ
- メンテナンス性を重視した継続可能なテスト設計
- 開発効率と品質のバランスを追求
- **Supabase PostgreSQL対応**: 本番環境と同等のテスト環境

## Supabase統合テスト詳細

### 新規追加：test_supabase_integration.py（7テスト）

#### 1. Supabase接続確認テスト（2個）
```python
def test_supabase_connection_with_valid_env():
    """有効な環境変数でSupabase接続成功テスト"""
    # 実際の環境変数が設定されている場合のみ実行
    # 接続テスト（SELECT 1クエリ実行）

def test_supabase_url_format_validation():
    """Supabase接続URL形式の検証テスト"""
    # PostgreSQL URL形式の正確性確認
    # 環境変数からのURL構築ロジック検証
```

#### 2. PostgreSQL CRUD操作テスト（2個）
```python
def test_postgresql_channel_operations():
    """PostgreSQLでのチャンネル操作テスト"""
    # CREATE, READ, UPDATE, DELETE の基本動作確認
    # 実PostgreSQL環境での動作検証

def test_postgresql_message_with_unicode():
    """PostgreSQLでの日本語メッセージ処理テスト"""
    # 日本語・絵文字を含むデータの処理確認
    # 文字エンコーディング・タイムゾーン処理の検証
```

#### 3. データベースフォールバック機能テスト（3個）
```python
def test_database_url_construction_logic():
    """データベースURL構築ロジックの検証テスト"""
    # 完全/不完全な環境変数設定での分岐確認
    # SQLiteフォールバック条件の検証

def test_sqlite_functionality_standalone():
    """SQLite機能の独立テスト"""
    # 基本的なSQLite動作確認
    # フォールバック時の動作保証

def test_environment_variable_validation():
    """環境変数バリデーションロジックのテスト"""
    # 必須環境変数の有無チェック
    # all()関数を使った検証ロジックの確認
```

### テスト実行の特徴
- **環境依存対応**: 環境変数未設定時は自動的にテストスキップ
- **接続失敗時の安全動作**: 実際のSupabaseに接続できない場合もテストが停止しない
- **開発効率重視**: ローカル開発環境でも支障なく動作

## AI機能特有のテスト考慮事項

### モック戦略
- **Google Gemini API**: 外部依存を避けるためモック使用
- **WebSocket通信**: リアルタイム性を保ったテスト設計
- **非同期処理**: AI応答の非同期性を考慮したテスト

### 将来の拡張
- **実際のAI API**: 統合テスト環境での実API テスト
- **応答品質テスト**: AI応答内容の品質評価
- **パフォーマンステスト**: AI応答速度の監視
