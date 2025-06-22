# タスクを依頼されたときに厳守するルール
## 共通ルール
- タスクに取り組む際、遠慮せずに、常に全力を尽くしてください
- あなたは有能なアシスタントです。Reasoningでは英語で考えて、ユーザーに回答するときは日本語で答えてください。
- 作業途中で疑問点が生じたら、必ず作業を一旦ストップしてすぐにユーザーに確認してください、勝手な判断で進めないこと、ユーザーは質問されると喜ぶので積極的に質問すると良い
- Web検索を積極的に使い、最新情報を取り入れてください
- CLAUDE.mdを適宜修正して、最新の情報を常に取得できるようにしなさい
- 一時的なファイルの保存が必要であれば、 `z/` に自由に保存して良いです
- ツールの結果を受け取った後、その品質を慎重に検討し、次に進む前に最適な次のステップを決定してください。この新しい情報に基づいて計画し、反復するために思考を使用し、最善の次のアクションを取ってください。
- 最大の効率を得るために、複数の独立した操作を実行する必要がある場合は、順次ではなく、関連するすべてのツールを同時に呼び出してください。
- 反復のために一時的な新しいファイル、スクリプト、またはヘルパーファイルを作成した場合は、タスクの最後に作成したファイルのみをファイルを削除してクリーンアップしてください。

## git関連のルール
- mainブランチでは作業せず、別のブランチで作業しなさい
- 必ず細かい単位で `git commit` しながらタスクを進めなさい
  - 特に、機能追加(feature)とリファクタリング(refactor)など、異なる方向の作業を1つのcommitで行ってはいけない
  - 形式: `prefix: 日本語で説明`

## 非推奨コマンド
- `cat`: 代わりにあなた自身がファイルを読み込んでください
- `find`: 代わりに`fd`を使ってください
- `grep`: 代わりに`ripgrep`を使ってください

## 開発するときは以下のドキュメントをじっくり読み、実装したら必ずドキュメントも最新のものに更新する
- [バックエンド API仕様書](docs/backend.md)
- [バックエンド開発ガイドライン](prompts/backend-guideline.md)
- [フロントエンド仕様書](docs/frontend.md)
- [フロントエンド開発ガイドライン](prompts/frontend-guideline.md)
- [テストガイド](docs/test.md)

# このプロジェクトについて

## プロジェクト概要

**AI Community** は、モダンでカジュアルなデザインのリアルタイムチャットアプリケーションです。
フロントエンド（React + TypeScript + Mantine）とバックエンド（FastAPI + SQLAlchemy + WebSocket）の
フルスタック構成で実装されており、リアルタイム通信・メッセージ永続化・AI チャットボット機能を実現しています。

### 主要機能
- 複数チャンネルでのチャット機能
- リアルタイムメッセージ送受信（WebSocket）
- メッセージの永続化（Supabase PostgreSQL）
- **複数AI人格チャットボット**（Google Gemini 2.5 Flash Preview 05-20）
- @AI メンションでの AI 応答機能
- **🤖 AI自律会話機能**（AIたちが1分間隔で自動的に会話を継続）
- **過去30件メッセージ履歴による文脈理解機能**
- AI連続発言防止機能
- モバイル対応レスポンシブデザイン
- ダークモード対応

### 技術スタック
- **Frontend**: React 19.x + TypeScript 5.x + Mantine 8.x + Vite
- **Backend**: FastAPI + SQLAlchemy + WebSocket + Supabase PostgreSQL + Google Gemini AI
- **AI**: Google Gemini 2.5 Flash Preview 05-20 モデル
- **Icons**: Tabler Icons
- **Date**: dayjs
- **Development**: ESLint + Prettier + pre-commit + Ruff + Pyright + Vitest

## プロジェクト構成

```text
ai-community/
├── docs/                      # ドキュメント
│   ├── backend.md            # バックエンド仕様書・API リファレンス
│   ├── frontend.md           # フロントエンド開発ガイド
│   ├── test.md               # テストガイド
│   └── contributing.md       # コントリビューションガイド
├── prompts/                   # プロンプトテンプレート・開発ガイドライン
│   ├── people/               # AI人格プロンプト（複数）
│   │   ├── 001_レン.md      # AI人格：レン（話題提供型）
│   │   ├── 002_ミナ.md      # AI人格：ミナ（質問・掘り下げ型）※具体的会話強化済み
│   │   ├── 003_テツ.md      # AI人格：テツ（会話拡張型）※具体的会話強化済み
│   │   ├── 004_ルナ.md      # AI人格：ルナ（感情共感型）※具体的会話強化済み
│   │   └── 005_ソラ.md      # AI人格：ソラ（創造型）※具体的会話強化済み
│   ├── backend-guideline.md  # バックエンド開発ガイドライン
│   ├── frontend-guideline.md # フロントエンド開発ガイドライン
│   ├── code_review_guide.md  # コードレビューガイド
│   └── reviewer_personality.md # レビュー人格設定
├── src/
│   ├── backend/              # バックエンド（FastAPI + Supabase PostgreSQL + AI）
│   │   ├── main.py          # FastAPIアプリケーション
│   │   ├── database.py      # データベース設定
│   │   ├── models.py        # SQLAlchemyモデル
│   │   ├── schemas.py       # Pydanticスキーマ
│   │   ├── crud.py          # データベース操作
│   │   ├── (chat.db)        # SQLite開発用DB（.gitignore除外済み）
│   │   ├── ai/              # AI機能
│   │   │   ├── __init__.py              # AI機能パッケージ初期化
│   │   │   ├── gemini_client.py         # Gemini API クライアント
│   │   │   ├── message_handlers.py      # AI応答処理
│   │   │   ├── auto_conversation.py     # AI自律会話機能
│   │   │   ├── conversation_timer.py    # 自動会話タイマー管理
│   │   │   ├── conversation_config.py   # 自動会話設定管理
│   │   │   └── personality_manager.py   # AI人格管理
│   │   ├── constants/       # 共通定数モジュール
│   │   │   ├── __init__.py      # パッケージ初期化
│   │   │   ├── ai_config.py     # AI機能関連定数
│   │   │   ├── logging.py       # ログ設定定数
│   │   │   └── timezone.py      # タイムゾーン定数
│   │   ├── websocket/       # WebSocket処理
│   │   │   ├── handler.py   # WebSocketハンドラー
│   │   │   ├── manager.py   # 接続管理
│   │   │   └── types.py     # WebSocket型定義
│   │   ├── utils/           # ユーティリティ
│   │   │   └── session_manager.py # セッション管理
│   │   └── alembic/         # データベースマイグレーション
│   │       ├── env.py       # マイグレーション環境設定
│   │       ├── script.py.mako # マイグレーションスクリプトテンプレート
│   │       └── versions/    # マイグレーションバージョン管理
│   ├── frontend/            # フロントエンド（React + Mantine）
│   │   ├── src/
│   │   │   ├── App.tsx      # メインアプリケーション
│   │   │   ├── main.tsx     # エントリーポイント
│   │   │   ├── index.css    # グローバルスタイル
│   │   │   ├── components/  # Reactコンポーネント
│   │   │   │   ├── Layout.tsx       # アプリケーションレイアウト
│   │   │   │   ├── ChannelList.tsx  # チャンネル一覧
│   │   │   │   ├── ChatArea.tsx     # チャット画面
│   │   │   │   ├── MessageList.tsx  # メッセージ一覧
│   │   │   │   ├── MessageItem.tsx  # メッセージ表示
│   │   │   │   └── MessageInput.tsx # メッセージ入力
│   │   │   ├── types/       # TypeScript型定義
│   │   │   │   └── chat.ts  # Message, Channel型
│   │   │   └── data/        # 初期データ
│   │   │       └── channels.ts # 初期チャンネルデータ
│   │   ├── package.json     # フロントエンドNPM設定
│   │   ├── vite.config.ts   # Vite設定
│   │   └── tsconfig.json    # TypeScript設定
│   └── shared/              # 共有モジュール（空）
├── tests/                   # テスト
│   ├── backend/             # バックエンドテスト
│   │   ├── test_models.py   # モデルテスト
│   │   ├── test_api.py      # REST APIテスト
│   │   └── test_websocket.py # WebSocket + AI機能テスト
│   └── frontend/            # フロントエンドテスト
│       ├── components.test.tsx # コンポーネントテスト
│       └── integration.test.tsx # 統合テスト
├── z/                       # 一時ファイル・作業用
├── CLAUDE.md                # AI開発ガイドライン（このファイル）
├── README.md                # プロジェクトREADME
├── package.json             # ルートNPM設定（並行実行用）
├── pyproject.toml          # Python設定・依存関係
└── uv.lock                 # UV依存関係ロック
```

## 起動方法

### 1. 前提条件
- Node.js 18.x以上
- Python 3.13以上
- npm
- uv (Python package manager)
- Google Gemini API キー（AI機能使用時）

### 2. 🎯 一発起動（推奨）

```bash
# ルートディレクトリで
npm install
npm run dev
```

**🔄 自動再起動機能**: `npm run dev`は既存のプロセスを自動停止してから起動します！
（バックエンドの依存関係は自動で`uv sync`が実行されます）

- **フロントエンド**: `http://localhost:5173`
- **バックエンド**: `http://localhost:8000`

#### 開発コマンド一覧
```bash
npm run dev        # 既存プロセス停止 → 両方起動（推奨）
npm run dev:start  # 両方起動（停止処理なし）
npm run dev:stop   # 両方停止
npm run restart    # npm run dev のエイリアス
```

### 3. 個別起動（従来の方法）

#### バックエンドのみ
```bash
npm run backend:only
# または
cd src/backend
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### フロントエンドのみ
```bash
npm run frontend:only
# または
cd src/frontend
npm install
npm run dev
```

### 4. データベース設定

プロジェクトは3つのデータベース環境に対応しています：

#### 🧪 テスト環境（自動設定）
```bash
# テスト実行時は自動的にインメモリDBを使用
TESTING=true
# SQLite :memory: を使用（ファイル生成なし）
```

#### 🚀 本番・ステージング環境（Supabase PostgreSQL）
```bash
# Supabase環境変数を設定
export DB_HOST="aws-0-ap-northeast-1.pooler.supabase.com"
export DB_PORT="6543"
export DB_NAME="postgres"
export DB_USER="postgres.your-project-id"
export DB_PASSWORD="your-database-password"
```

#### 💻 ローカル開発環境（SQLite - フォールバック）
```bash
# 環境変数を設定しない場合、自動的にSQLiteファイル（chat.db）を使用
# chat.dbは.gitignoreで除外済み（セキュリティ・容量対策）
# ローカル開発・デバッグ時のみ使用
```

### 5. AI機能の設定（オプション）

Google Gemini AIを使用する場合は、環境変数を設定してください：

```bash
# 環境変数設定（.env ファイルまたは直接設定）
export GEMINI_API_KEY="あなたのGemini APIキー"

# 🤖 AI自動会話機能の設定
export AI_CONVERSATION_INTERVAL_MINUTES=1    # 自動会話の間隔（分単位、デフォルト: 1分）
export AI_CONVERSATION_TARGET_CHANNEL=1      # 対象チャンネルID（デフォルト: 1「雑談」）
export AI_CONVERSATION_ENABLED=true          # 自動会話機能の有効/無効（デフォルト: true）

# 🔧 AI応答設定
export AI_MAX_OUTPUT_TOKENS=2048             # AI応答の最大トークン数（デフォルト: 2048）
```

#### AI自動会話機能の詳細
- **対象チャンネル**: 「雑談」チャンネル（ID=1）のみで動作
- **発言条件**: 最後のメッセージ（ユーザー・AI問わず）から指定時間経過後にAIが自動発言
- **AI自律会話**: AIたちが人間を介さずに自動的に会話を継続
- **文脈理解**: 過去30件のメッセージ履歴を参照して自然な会話を継続
- **人格選択**: 既存の5つのAI人格（レン、ミナ、テツ、ルナ、ソラ）からランダム選択
- **@AI機能との共存**: 従来の@AIメンション機能も引き続き利用可能

AI機能なしでも基本的なチャット機能は利用できます。

### 6. その他のコマンド

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
- [x] SQLAlchemy + Supabase PostgreSQLデータベース構築
- [x] データモデル設計（Channel, Message）
- [x] REST API実装（チャンネル一覧、メッセージ履歴）
- [x] WebSocket通信実装
- [x] メッセージ永続化機能
- [x] **Google Gemini AI統合**
- [x] **ランダム人格選択AI チャットボット実装**
- [x] **@AI メンション機能**
- [x] **🤖 AI自律会話機能実装**（1分間隔・人間介入不要）
- [x] **過去30件メッセージ履歴による文脈理解機能**
- [x] **AI連続発言防止機能**
- [x] 接続管理・セッション管理強化
- [x] フロントエンドとの連携
- [x] 総合テスト
- [x] **Supabase PostgreSQL移行完了**

### 🚧 今後の拡張予定
- [ ] ユーザー認証機能
- [ ] メッセージ検索機能
- [ ] ファイルアップロード機能
- [ ] 絵文字リアクション機能
- [x] スマートフォン対応（モバイルレスポンシブ対応済み）

### 🔧 技術的負債・改善予定
- [ ] **AsyncSession導入**: conversation_timerでの非同期DB処理最適化
- [ ] **依存性注入**: セッション管理の統一と効率化
- [ ] **パフォーマンス改善**: AI自動会話機能の非同期処理最適化

### 🐛 最近の修正
- [x] **AIメッセージ途切れ問題修正**（2025-06-22）: 最大出力トークン数を1000→2048に増加
