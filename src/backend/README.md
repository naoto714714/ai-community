# AI Community Backend

シンプルなチャットアプリケーションのバックエンド実装

## 📁 プロジェクト構造

```
src/backend/
├── __init__.py          # パッケージ初期化
├── main.py              # FastAPIアプリケーションのエントリーポイント
├── database.py          # データベース接続設定
├── models.py            # SQLAlchemyモデル定義
├── schemas.py           # Pydanticスキーマ
├── crud.py              # データベース操作
├── websocket.py         # WebSocket処理
├── constants.py         # 定数定義
├── pyproject.toml       # プロジェクト設定
├── uv.lock              # 依存関係ロック
└── README.md            # このファイル
```

## 🚀 開発環境セットアップ

```bash
# バックエンドディレクトリに移動
cd src/backend

# 依存関係をインストール
uv sync

# 開発サーバーを起動
uv run uvicorn main:app --reload --port 8000
```

## 📋 実装予定機能

### ステップ1: 環境セットアップ ✅
- [x] プロジェクト構造作成
- [x] Python 3.13環境設定
- [x] 依存関係設定

### ステップ2: データベース設定
- [ ] SQLAlchemyモデル定義
- [ ] データベース初期化
- [ ] 初期チャンネル作成

### ステップ3: 基本API
- [ ] チャンネル一覧取得
- [ ] メッセージ履歴取得
- [ ] メッセージ作成

### ステップ4: WebSocket
- [ ] リアルタイムメッセージ配信
- [ ] 接続管理

## 🔧 技術スタック

- **Python**: 3.13
- **フレームワーク**: FastAPI
- **データベース**: SQLite（ローカルファイル）
- **ORM**: SQLAlchemy 2.0
- **WebSocket**: FastAPI内蔵サポート
- **ASGIサーバー**: uvicorn

## 🗄️ データモデル

### Channel
- id: str (主キー)
- name: str (チャンネル名)
- created_at: datetime

### Message  
- id: str (主キー)
- channel_id: str (外部キー)
- user_id: str
- user_name: str
- content: str (メッセージ内容)
- timestamp: datetime
- is_own_message: bool
- created_at: datetime

## 🔗 API仕様

### REST API
- `GET /api/channels` - チャンネル一覧取得
- `GET /api/channels/{channel_id}/messages` - メッセージ履歴取得

### WebSocket
- `ws://localhost:8000/ws` - リアルタイム通信

## 📝 開発ルール

- 型ヒントを必ず記述
- docstringをパブリック関数に追加
- テストコードを併せて実装
- コミットは細かい単位で実行