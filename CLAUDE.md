# タスクを依頼されたときに厳守するルール
## 共通ルール
- タスクに取り組む際、遠慮せずに、常に全力を尽くしてください
- Web検索を積極的に使い、最新情報を取り入れてください
- 待機状態に戻る前に `afplay /Users/kimuranaoto/Music/notice.mp3` を必ず実行しなさい
- CLAUDE.mdを適宜修正して、最新の情報を常に取得できるようにしなさい
- 一時的なファイルの保存が必要であれば、 `z/` に自由に保存して良いです
- ツールの結果を受け取った後、その品質を慎重に検討し、次に進む前に最適な次のステップを決定してください。この新しい情報に基づいて計画し、反復するために思考を使用し、最善の次のアクションを取ってください。
- 最大の効率を得るために、複数の独立した操作を実行する必要がある場合は、順次ではなく、関連するすべてのツールを同時に呼び出してください。
- 反復のために一時的な新しいファイル、スクリプト、またはヘルパーファイルを作成した場合は、タスクの最後にこれらのファイルを削除してクリーンアップしてください。

## git関連のルール
- mainブランチでは作業せず、別のブランチで作業しなさい
- 必ず細かい単位で `git commit` しながらタスクを進めなさい
  - 特に、機能追加(feature)とリファクタリング(refactor)など、異なる方向の作業を1つのcommitで行ってはいけない
  - 形式: `prefix: 日本語で説明`

# このプロジェクトについて

## プロジェクト概要

**AI Community** は、モダンでカジュアルなデザインのリアルタイムチャットアプリケーションです。
フロントエンド（React + TypeScript + Mantine）とバックエンド（FastAPI + SQLAlchemy + WebSocket）の
フルスタック構成で実装されており、リアルタイム通信とメッセージ永続化を実現しています。

### 主要機能
- 複数チャンネルでのチャット機能
- リアルタイムメッセージ送受信（WebSocket）
- メッセージの永続化（SQLite）
- レスポンシブデザイン（PC版優先）
- ダークモード対応

### 技術スタック
- **Frontend**: React 18.x + TypeScript 5.x + Mantine 7.x + Vite
- **Backend**: FastAPI + SQLAlchemy + WebSocket + SQLite
- **Icons**: Tabler Icons
- **Date**: dayjs
- **Development**: ESLint + Prettier + pre-commit + Ruff + Pyright

## プロジェクト構成

```
ai-community/
├── docs/                      # ドキュメント
│   ├── chat-app-spec.md      # フロントエンド仕様書
│   ├── backend-implementation-guide.md  # バックエンド実装手順書
│   ├── simple-backend-spec.md           # バックエンド仕様書
│   ├── frontend-guideline.md           # フロントエンド開発ガイドライン
│   └── backend-guideline.md            # バックエンド開発ガイドライン
├── src/
│   ├── backend/              # バックエンド（FastAPI + SQLite）
│   │   ├── main.py          # FastAPIアプリケーション
│   │   ├── models.py        # SQLAlchemyモデル
│   │   ├── database.py      # データベース設定
│   │   ├── schemas.py       # Pydanticスキーマ
│   │   ├── websocket.py     # WebSocket処理
│   │   ├── crud.py          # データベース操作
│   │   └── chat.db          # SQLiteデータベース
│   └── frontend/            # フロントエンド（React + Mantine）
│       ├── src/
│       │   ├── components/  # Reactコンポーネント
│       │   ├── types/       # TypeScript型定義
│       │   └── data/        # 初期データ
│       └── package.json     # NPM設定
├── tests/                   # テスト（Python）
├── prompts/                 # プロンプトテンプレート
├── z/                       # 一時ファイル
├── CLAUDE.md                # AI開発ガイドライン（このファイル）
├── README.md                # プロジェクトREADME
├── .gitignore              # Git除外設定
├── .pre-commit-config.yaml # pre-commit設定
├── pyproject.toml          # Python設定
└── uv.lock                 # UV依存関系ロック
```

## 起動方法

### 1. 前提条件
- Node.js 18.x以上
- Python 3.13以上
- npm
- uv (Python package manager)

### 2. バックエンド起動
```bash
# バックエンドディレクトリに移動
cd src/backend

# 依存関係インストール（初回のみ）
uv sync

# 開発サーバー起動
uv run python main.py
```

バックエンドAPI: `http://localhost:8000`

### 3. フロントエンド起動（別ターミナル）
```bash
# フロントエンドディレクトリに移動
cd src/frontend

# 依存関係インストール（初回のみ）
npm install

# 開発サーバー起動
npm run dev
```

フロントエンド: `http://localhost:5173`

### 4. その他のコマンド

#### フロントエンド
```bash
npm run build      # ビルド
npm run preview    # プレビュー
npm run lint       # ESLintチェック
```

#### バックエンド
```bash
uv run --frozen ruff format .    # コードフォーマット
uv run --frozen ruff check .     # リントチェック
uv run --frozen pyright          # 型チェック
```

## 開発状況

### ✅ フロントエンド（完了済み）
- [x] プロジェクト初期セットアップ
- [x] Vite + React + TypeScript環境構築
- [x] Mantine UIライブラリ導入
- [x] 基本設定・動作確認
- [x] 基本レイアウト構築（AppShell）
- [x] チャンネル一覧実装
- [x] メッセージ入力欄実装
- [x] メッセージ表示機能
- [x] WebSocket通信実装
- [x] 最終調整とスタイリング

### ✅ バックエンド（完了済み）
- [x] FastAPI環境セットアップ
- [x] SQLAlchemy + SQLiteデータベース構築
- [x] データモデル設計（Channel, Message）
- [x] REST API実装（チャンネル一覧、メッセージ履歴）
- [x] WebSocket通信実装
- [x] メッセージ永続化機能
- [x] フロントエンドとの連携
- [x] 総合テスト

### 🚧 今後の拡張予定
- [ ] ユーザー認証機能
- [ ] メッセージ検索機能
- [ ] ファイルアップロード機能
- [ ] 絵文字リアクション機能
- [ ] スマートフォン対応

## デザイン仕様

- **レイアウト**: 左サイドバー（280px）+ メインエリア
- **カラーテーマ**: ダークモード対応（Mantineデフォルト）
- **アクセントカラー**: blue/violet系
- **フォント**: システムフォント（-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP'）
- **最小幅**: 1024px（PC版優先）

- Frontend開発ガイドライン: @docs/frontend-guideline.md
- Backend開発ガイドライン: @docs/backend-guideline.md
