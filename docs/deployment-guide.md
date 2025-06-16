# デプロイ・運用ガイド

## 概要

AI Community アプリケーションの本番環境デプロイと運用に関するガイドです。
現在は開発環境向けの設定ですが、本番環境への移行を想定した手順も含めています。

## 開発環境セットアップ

### 前提条件

- **Node.js**: 18.x 以上
- **Python**: 3.13 以上  
- **uv**: Python パッケージマネージャー
- **Git**: バージョン管理

### クイックスタート

```bash
# リポジトリクローン
git clone <repository-url>
cd ai-community

# バックエンドセットアップ
cd src/backend
uv sync
uv run python main.py &

# フロントエンドセットアップ（別ターミナル）
cd src/frontend
npm install
npm run dev
```

アクセス:
- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## 本番環境デプロイ

### バックエンドデプロイ

#### Docker を使用した場合

```dockerfile
# Dockerfile (backend)
FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY . .
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
# ビルド・実行
docker build -t ai-community-backend .
docker run -p 8000:8000 -v ./chat.db:/app/chat.db ai-community-backend
```

#### 直接デプロイ

```bash
# 本番環境での起動
cd src/backend
uv sync --frozen
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### フロントエンドデプロイ

#### 静的ファイル生成

```bash
cd src/frontend
npm ci
npm run build

# dist/ フォルダを Webサーバーに配置
# 例: Nginx, Apache, CDN など
```

#### Docker を使用した場合

```dockerfile
# Dockerfile (frontend)
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

### 環境変数設定

#### バックエンド (.env)

```bash
# データベース設定
DATABASE_URL=sqlite:///./chat.db  # 開発環境
# DATABASE_URL=postgresql://user:pass@host:port/dbname  # 本番環境

# CORS設定
ALLOWED_ORIGINS=http://localhost:5173,https://yourdomain.com

# ログレベル
LOG_LEVEL=INFO

# セキュリティ
SECRET_KEY=your-secret-key-here
```

#### フロントエンド (.env)

```bash
# API エンドポイント
VITE_API_BASE_URL=http://localhost:8000  # 開発環境
# VITE_API_BASE_URL=https://api.yourdomain.com  # 本番環境

VITE_WS_URL=ws://localhost:8000/ws  # 開発環境
# VITE_WS_URL=wss://api.yourdomain.com/ws  # 本番環境
```

## データベース管理

### SQLite（開発・小規模運用）

```bash
# データベースファイルの確認
ls -la src/backend/chat.db

# SQLite コマンドラインでの操作
cd src/backend
sqlite3 chat.db

# SQL実行例
.tables                           # テーブル一覧
SELECT * FROM channels;           # チャンネル一覧
SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;  # 最新メッセージ
.quit
```

### PostgreSQL（本番環境推奨）

```bash
# マイグレーション（将来対応）
# DATABASE_URL を PostgreSQL に変更後
uv run alembic upgrade head
```

### データバックアップ

```bash
# SQLite バックアップ
cp src/backend/chat.db backups/chat_$(date +%Y%m%d_%H%M%S).db

# PostgreSQL バックアップ（将来対応）
pg_dump -h localhost -U username dbname > backup.sql
```

## 監視・ログ

### ログファイル確認

```bash
# バックエンドログ
cd src/backend
uv run python main.py 2>&1 | tee app.log

# アクセスログ分析
grep "WebSocket" app.log
grep "ERROR" app.log
```

### ヘルスチェック

```bash
# API 動作確認
curl -f http://localhost:8000/ || echo "Backend is down"
curl -f http://localhost:8000/api/channels || echo "API is down"

# WebSocket 接続確認
cd src/backend
uv run python test_websocket.py
```

### モニタリング指標

- **応答時間**: API レスポンス時間
- **接続数**: WebSocket アクティブ接続数
- **エラー率**: 4xx/5xx エラーの発生率
- **データベース**: 接続プール使用率
- **ディスク容量**: SQLite ファイルサイズ

## トラブルシューティング

### よくある問題

#### 1. WebSocket 接続エラー

**症状**: フロントエンドでメッセージ送信ができない

**確認点**:
```bash
# バックエンドが起動しているか
curl http://localhost:8000/

# WebSocket エンドポイントが有効か
# ブラウザ開発者ツールでコンソールエラーを確認
```

**解決方法**:
- バックエンドサーバーの再起動
- CORS設定の確認
- ファイアウォール設定の確認

#### 2. データベース接続エラー

**症状**: `sqlite3.OperationalError: database is locked`

**解決方法**:
```bash
# プロセス確認・終了
ps aux | grep python
kill <PID>

# データベースファイル権限確認
chmod 644 src/backend/chat.db
```

#### 3. フロントエンドビルドエラー

**症状**: `npm run build` が失敗する

**解決方法**:
```bash
# 依存関係再インストール
rm -rf node_modules package-lock.json
npm install

# TypeScript エラー確認
npm run build 2>&1 | grep "error TS"
```

#### 4. メモリ使用量増加

**原因**: WebSocket接続のリーク

**対処法**:
```bash
# 接続数確認
ss -tln | grep :8000

# アプリケーション再起動
cd src/backend
pkill -f "python main.py"
uv run python main.py
```

### ログ分析

```bash
# エラーパターン分析
grep -E "(ERROR|CRITICAL)" app.log | sort | uniq -c

# WebSocket接続パターン
grep "WebSocket" app.log | awk '{print $3}' | sort | uniq -c

# レスポンス時間分析（将来対応）
grep "response_time" app.log | awk '{sum+=$4; count++} END {print "平均:", sum/count "ms"}'
```

## セキュリティ

### 現在の対策

- **CORS**: 特定オリジンのみ許可
- **入力検証**: Pydantic によるバリデーション
- **SQLインジェクション**: SQLAlchemy ORM使用

### 推奨追加対策

```python
# レート制限 (slowapi)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.add_middleware(SlowAPIMiddleware)

@app.post("/api/messages")
@limiter.limit("10/minute")
async def send_message(request: Request, ...):
    pass
```

```python
# 入力サイズ制限
from fastapi import Request, HTTPException

@app.middleware("http")
async def limit_upload_size(request: Request, call_next):
    if request.url.path.startswith("/api/"):
        if "content-length" in request.headers:
            if int(request.headers["content-length"]) > 1_000_000:  # 1MB
                raise HTTPException(413, "Request too large")
    return await call_next(request)
```

## バックアップ・復旧

### 定期バックアップスクリプト

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_FILE="src/backend/chat.db"

mkdir -p $BACKUP_DIR

# データベースバックアップ
cp $DB_FILE $BACKUP_DIR/chat_$DATE.db

# 古いバックアップ削除（30日以上）
find $BACKUP_DIR -name "chat_*.db" -mtime +30 -delete

echo "Backup completed: chat_$DATE.db"
```

```bash
# cron 設定例（毎日午前2時）
0 2 * * * /path/to/ai-community/backup.sh
```

### 復旧手順

```bash
# 1. サービス停止
pkill -f "python main.py"
pkill -f "npm run dev"

# 2. データベース復旧
cp backups/chat_YYYYMMDD_HHMMSS.db src/backend/chat.db

# 3. 権限設定
chmod 644 src/backend/chat.db

# 4. サービス再開
cd src/backend && uv run python main.py &
cd src/frontend && npm run dev &
```

## パフォーマンス最適化

### バックエンド最適化

```python
# データベース接続プール（将来対応）
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=300
)
```

```python
# 非同期対応（将来対応）
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

async def get_async_db():
    async with AsyncSession(async_engine) as session:
        yield session
```

### フロントエンド最適化

```typescript
// メッセージの仮想スクロール（将来対応）
import { FixedSizeList as List } from 'react-window';

// メモ化最適化
const MessageItem = React.memo(({ message }: { message: Message }) => {
  return <div>{message.content}</div>;
});
```

## アップデート手順

### バックエンドアップデート

```bash
# 1. バックアップ作成
./backup.sh

# 2. コード更新
git pull origin main

# 3. 依存関係更新
cd src/backend
uv sync

# 4. データベースマイグレーション（将来対応）
uv run alembic upgrade head

# 5. 再起動
pkill -f "python main.py"
uv run python main.py
```

### フロントエンドアップデート

```bash
# 1. コード更新
git pull origin main

# 2. 依存関係更新
cd src/frontend
npm ci

# 3. ビルド・デプロイ
npm run build
# 生成された dist/ を本番サーバーに配置
```