# バックエンド実装詳細

## 概要

AI Community バックエンドは、FastAPI を使用した RESTful API と WebSocket によるリアルタイム通信を提供します。
SQLAlchemy + SQLite でデータ永続化を行い、チャンネル管理とメッセージ機能を実現しています。

## 技術構成

### コア技術
- **FastAPI**: Webフレームワーク（高性能・自動ドキュメント生成）
- **SQLAlchemy 2.0**: ORM（データベース操作）
- **SQLite**: データベース（ファイルベース・開発用）
- **WebSocket**: リアルタイム通信
- **Pydantic**: データバリデーション・シリアライゼーション
- **Python**: 3.13

### 開発ツール
- **uv**: Pythonパッケージマネージャー
- **Ruff**: 高速リンター・フォーマッター
- **Pyright**: 型チェッカー

## プロジェクト構造

```
src/backend/
├── main.py                 # FastAPIアプリケーション・エントリーポイント
├── models.py               # SQLAlchemyデータモデル
├── database.py             # データベース設定・接続管理
├── schemas.py              # Pydanticスキーマ（APIリクエスト・レスポンス）
├── crud.py                 # データベース操作関数
├── websocket.py            # WebSocket接続管理・メッセージ処理
├── test_websocket.py       # WebSocketテスト用スクリプト
├── test_comprehensive.py   # 総合テストスイート
├── pyproject.toml          # プロジェクト設定・依存関係
├── uv.lock                 # 依存関係ロックファイル
└── chat.db                 # SQLiteデータベースファイル
```

## データモデル

### Channel モデル

```python
class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
```

**用途**: チャンネル情報の管理
**フィールド**:
- `id`: チャンネル一意識別子
- `name`: チャンネル表示名
- `created_at`: 作成日時（UTC）

### Message モデル

```python
class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    channel_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    user_name: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    is_own_message: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(UTC))
```

**用途**: メッセージデータの永続化
**フィールド**:
- `id`: メッセージ一意識別子
- `channel_id`: 所属チャンネルID（インデックス付き）
- `user_id`: 送信者ID
- `user_name`: 送信者表示名
- `content`: メッセージ本文
- `timestamp`: 送信時刻
- `is_own_message`: 送信者自身のメッセージかどうか
- `created_at`: データベース挿入時刻（UTC）

## API スキーマ

### Pydantic モデル設計

#### alias_generator の実装
フロントエンド（camelCase）とバックエンド（snake_case）の命名規則橋渡し:

```python
def to_camel(string: str) -> str:
    """Convert snake_case to camelCase"""
    components = string.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])
```

#### MessageCreate (リクエスト)
```python
class MessageCreate(MessageBase):
    # 継承により全フィールドを含む
    pass
```

#### MessageResponse (レスポンス)
```python
class MessageResponse(MessageBase):
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, ...)
```

#### MessagesListResponse (ページネーション)
```python
class MessagesListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int
    has_more: bool
```

## REST API エンドポイント

### GET / (ルート)
**用途**: APIサーバー動作確認
**レスポンス**: `{"message": "AI Community Backend API"}`

### GET /api/channels
**用途**: 全チャンネル一覧取得
**レスポンス**: `List[ChannelResponse]`

```json
[
  {"id": "1", "name": "雑談", "createdAt": "2024-01-01T00:00:00Z"},
  {"id": "2", "name": "ゲーム", "createdAt": "2024-01-01T00:00:00Z"}
]
```

### GET /api/channels/{channel_id}/messages
**用途**: 指定チャンネルのメッセージ履歴取得
**パラメータ**:
- `channel_id`: チャンネルID（パス）
- `limit`: 取得件数上限（クエリ、デフォルト100）
- `offset`: 取得開始位置（クエリ、デフォルト0）

**レスポンス**: `MessagesListResponse`

```json
{
  "messages": [
    {
      "id": "msg_123",
      "channelId": "1",
      "userId": "user_456",
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

## WebSocket 通信

### エンドポイント
`ws://localhost:8000/ws`

### 接続管理 (ConnectionManager)

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket)
    def disconnect(self, websocket: WebSocket)
    async def send_personal_message(self, message: str, websocket: WebSocket)
    async def broadcast(self, message: str)
```

**機能**:
- アクティブ接続の管理
- 個別メッセージ送信
- ブロードキャスト送信
- 切断時のクリーンアップ

### メッセージプロトコル

#### メッセージ送信リクエスト
```json
{
  "type": "message:send",
  "data": {
    "id": "msg_123",
    "channel_id": "1",
    "user_id": "user_456",
    "user_name": "ユーザー",
    "content": "こんにちは",
    "timestamp": "2024-01-01T12:00:00Z",
    "is_own_message": true
  }
}
```

#### 成功レスポンス
```json
{
  "type": "message:saved",
  "data": {
    "id": "msg_123",
    "success": true
  }
}
```

#### エラーレスポンス
```json
{
  "type": "message:error",
  "data": {
    "id": "msg_123",
    "success": false,
    "error": "エラーメッセージ"
  }
}
```

## CRUD 操作

### create_message()
**用途**: 新しいメッセージをデータベースに保存
**エラーハンドリング**: トランザクションロールバック対応

### get_channel_messages()
**用途**: 指定チャンネルのメッセージ一覧取得
**特徴**:
- ページネーション対応（skip/limit）
- 作成日時昇順ソート
- パラメータバリデーション

### get_channel_messages_count()
**用途**: 指定チャンネルのメッセージ総数取得
**利用場面**: ページネーション計算

### get_channels()
**用途**: 全チャンネル一覧取得

## データベース設定

### 接続設定 (database.py)
```python
SQLALCHEMY_DATABASE_URL = "sqlite:///./chat.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### セッション管理
```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

FastAPI の依存性注入システムと連携してセッション管理を自動化。

### 初期化処理 (lifespan)

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時処理
    Base.metadata.create_all(bind=engine)  # テーブル作成
    init_channels()  # 初期チャンネル作成
    yield
    # 終了時処理
```

**機能**:
- アプリケーション起動時のテーブル自動作成
- 初期チャンネルデータの挿入
- グレースフルシャットダウン対応

## 設定・デプロイ

### 依存関係 (pyproject.toml)

```toml
[project]
name = "ai-community-backend"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.0",
    "sqlalchemy>=2.0.25",
    "websockets>=12.0",
]
```

### CORS 設定

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

フロントエンド（localhost:5173）からのアクセスを許可。

### ログ設定

```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

WebSocket接続・メッセージ処理のログ出力。

## 開発ワークフロー

### 起動方法

```bash
cd src/backend
uv sync                    # 依存関係インストール
uv run python main.py      # 開発サーバー起動
```

### コード品質管理

```bash
uv run --frozen ruff format .     # コードフォーマット
uv run --frozen ruff check .      # リンティング
uv run --frozen pyright           # 型チェック
```

### テスト実行

```bash
# WebSocket機能テスト
uv run python test_websocket.py

# 総合テスト
uv run --frozen pytest test_comprehensive.py
```

## API ドキュメント

FastAPI 自動生成ドキュメント:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## エラーハンドリング

### WebSocket エラー処理

```python
try:
    message_create = MessageCreate(**message_data)
    saved_message = crud.create_message(db, message_create)
    # 成功レスポンス
except Exception as e:
    logger.error(f"Error saving message: {str(e)}")
    # エラーレスポンス
finally:
    db.close()
```

### HTTP エラー処理

```python
# チャンネル存在確認
channel = db.query(Channel).filter(Channel.id == channel_id).first()
if not channel:
    raise HTTPException(status_code=404, detail="Channel not found")
```

## セキュリティ考慮事項

### 現在の対策
- SQLインジェクション対策（SQLAlchemy ORM使用）
- CORS設定による アクセス制御
- Pydantic によるデータバリデーション

### 今後の強化予定
- [ ] JWT認証システム
- [ ] レート制限
- [ ] 入力サイズ制限
- [ ] ログ監査機能

## パフォーマンス最適化

### データベース
- `channel_id` フィールドにインデックス設定
- 効率的なクエリ設計（必要最小限の取得）

### WebSocket
- 接続プール管理
- 切断済み接続の自動クリーンアップ

### 今後の最適化予定
- [ ] データベース接続プーリング
- [ ] メッセージのページネーション改善
- [ ] Redis によるセッション管理
- [ ] 非同期ログ処理

## 拡張予定機能

### 近期実装
- [ ] ユーザー認証・セッション管理
- [ ] メッセージ検索API
- [ ] ファイルアップロード機能
- [ ] リアルタイム通知

### 長期実装
- [ ] マルチテナント対応
- [ ] メッセージ暗号化
- [ ] 音声・ビデオ通話
- [ ] 分散アーキテクチャ対応

## 運用・監視

### ログ監視
- WebSocket接続数追跡
- エラー発生率監視
- レスポンス時間計測

### ヘルスチェック
```bash
curl http://localhost:8000/     # 基本動作確認
curl http://localhost:8000/api/channels  # API動作確認
```

### バックアップ
```bash
# SQLiteデータベースのバックアップ
cp chat.db chat_backup_$(date +%Y%m%d_%H%M%S).db
```
