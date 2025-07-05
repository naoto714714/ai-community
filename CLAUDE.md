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
- リファクタリングはMartin Fowlerが推奨する進め方に従ってください。

## git関連のルール
- mainブランチでは作業せず、別のブランチで作業しなさい
- 必ず細かい単位で `git commit` しながらタスクを進めなさい
  - 特に、機能追加(feature)とリファクタリング(refactor)など、異なる方向の作業を1つのcommitで行ってはいけない
  - 形式: `prefix: 日本語で説明`

## Gemini Search
`gemini` is google gemini cli. **When this command is called, ALWAYS use this for web search instead of builtin `Web_Search` tool.**
When web search is needed, you MUST use `gemini --prompt` via Task Tool.
Run web search via Task Tool with `gemini --prompt 'WebSearch: <query>'`

```bash
gemini --prompt "WebSearch: <query>"
```

## 非推奨コマンド
- `cat`: 代わりにあなた自身がファイルを読み込んでください
- `find`: 代わりに`fd`を使ってください
- `grep`: 代わりに`ripgrep`を使ってください

## 開発するときは以下のドキュメントをじっくり読み、実装したら必ずドキュメントも最新のものに更新する
- [バックエンド API仕様書](docs/backend.md)
- [バックエンド開発ガイドライン](prompts/backend-guideline.md) // 更新禁止
- [フロントエンド仕様書](docs/frontend.md)
- [フロントエンド開発ガイドライン](prompts/frontend-guideline.md) // 更新禁止
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
- **🤖 AI自律会話機能**（AIたちが自動的に会話を継続）
- **過去10件メッセージ履歴による文脈理解機能**
- AI連続発言防止機能
- モバイル対応レスポンシブデザイン
- ダークモード対応

### 技術スタック
- **Frontend**: React 19.x + TypeScript 5.x + Mantine 8.x + Vite
- **Backend**: FastAPI + SQLAlchemy + WebSocket + Supabase PostgreSQL + Google Gemini AI
- **AI**: Google Gemini 2.5 Flash Preview 05-20 モデル
- **Icons**: Tabler Icons
- **Date**: dayjs
- **Development**: ESLint + Prettier + **Pre-commit Hooks** + Ruff + Pyright + Vitest + **MCP Playwright**

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

### 4. データベース設定

#### 🚀 Supabase PostgreSQL（本番・開発環境）
```bash
# Supabase環境変数を設定
export DB_HOST="aws-0-ap-northeast-1.pooler.supabase.com"
export DB_PORT="6543"
export DB_NAME="postgres"
export DB_USER="postgres.your-project-id"
export DB_PASSWORD="your-database-password"
```

#### 🧪 テスト環境（自動設定）
```bash
# テスト実行時は自動的にインメモリDBを使用
TESTING=true
# PostgreSQL :memory: を使用（ファイル生成なし）
```


### 5. AI機能の設定（オプション）

Google Gemini AIを使用する場合は、環境変数を設定してください：

```bash
# 環境変数設定（.env ファイルまたは直接設定）
export GEMINI_API_KEY="あなたのGemini APIキー"

# 🤖 AI自動会話機能の設定
export AI_CONVERSATION_INTERVAL_SECONDS=60   # 自動会話の間隔（秒単位、デフォルト: 60秒、範囲: 1-86400秒）
export AI_CONVERSATION_TARGET_CHANNEL=1      # 対象チャンネルID（デフォルト: 1「雑談」）
export AI_CONVERSATION_ENABLED=true          # 自動会話機能の有効/無効（デフォルト: true）

# 🔧 AI応答設定
export AI_MAX_OUTPUT_TOKENS=2048             # AI応答の最大トークン数（デフォルト: 2048）
```

#### AI自動会話機能の詳細
- **対象チャンネル**: 「雑談」チャンネル（ID=1）のみで動作
- **発言条件**: 最後のメッセージ（ユーザー・AI問わず）から指定時間経過後にAIが自動発言
- **AI自律会話**: AIたちが人間を介さずに自動的に会話を継続
- **文脈理解**: 過去10件のメッセージ履歴を参照して自然な会話を継続
- **人格選択**: 複数のAI人格からランダム選択
- **共通プロンプト機能**: 全AI人格に共通の基本ルールを適用（日本語使用、自然な会話、適度な長さ等）
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
- [x] **人間っぽくプロンプト変更・AI自然化**（2025-06-25）: 共通プロンプト機能追加、AI自動会話プロンプト簡素化、会話履歴表示の自然化、AI人格ファイル配置修正
- [x] **Pre-commit最適化・コード品質向上**（2025-06-23）: 包括的なフック設定、Discord Webhook機能、ドキュメント全面強化、型安全性向上
- [x] **AIメッセージ途切れ問題修正**（2025-06-22）: 最大出力トークン数を1000→2048に増加
