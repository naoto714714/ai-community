# AI Community

**複数AI人格チャットボット搭載**のモダンなリアルタイムチャットアプリケーション。フロントエンド（React）とバックエンド（FastAPI）のフルスタック構成で実装されています。

## 📋 プロジェクト概要

このプロジェクトは、React + TypeScript + Mantineを使用したフロントエンドと、FastAPI + SQLAlchemy + WebSocketを使用したバックエンドで構成されるチャットアプリケーションです。
リアルタイム通信・メッセージの永続化・AI チャットボット機能を実現しています。

### 主要機能

- 複数チャンネルでのチャット機能
- リアルタイムメッセージ送受信（WebSocket）
- メッセージの永続化（Supabase PostgreSQL）
- **🤖 複数AI人格チャットボット**（Google Gemini 2.5 Flash Preview 05-20）
  - **5つのAI人格**: レン（話題提供型）、ミナ（質問・掘り下げ型）、テツ（会話拡張型）、ルナ（感情共感型）、ソラ（創造型）
  - **具体的で質の高い会話**: 抽象的ではなく具体的な話題で自然な対話を実現
- **@AI メンションでの AI 応答機能**
- **🤖 AI自律会話機能**（AIたちが設定間隔で自動的に会話を継続、デフォルト60秒）
- **過去10件メッセージ履歴による文脈理解機能**
- AI連続発言防止機能
- モバイル対応レスポンシブデザイン
- ダークモード対応

## 🛠 技術スタック

### フロントエンド
- **React**: 19.x
- **TypeScript**: 5.x
- **Mantine**: 8.x（UIコンポーネントライブラリ）
- **Mantine Hooks**: カスタムフック集
- **Tabler Icons**: アイコンライブラリ
- **Vite**: ビルドツール
- **dayjs**: 日付処理

### バックエンド
- **FastAPI**: Webフレームワーク
- **SQLAlchemy**: ORM
- **Supabase PostgreSQL**: データベース
- **WebSocket**: リアルタイム通信
- **Pydantic**: データバリデーション
- **Google Gemini AI**: AI チャットボット
- **Python**: 3.13

### 開発環境
- **ESLint**: コード品質管理（フロントエンド）
- **Prettier**: コードフォーマット
- **Vitest**: テストフレームワーク（フロントエンド）
- **Ruff**: リンター・フォーマッター（バックエンド）
- **Pyright**: 型チェッカー（バックエンド）
- **pre-commit**: Gitフック管理
- **uv**: Pythonパッケージマネージャー

## 🚀 セットアップ・起動方法

### 1. 前提条件

- Node.js 18.x以上
- Python 3.13以上
- npm
- uv (Python package manager)
- Google Gemini API キー（AI機能使用時、オプション）

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

#### 便利な開発コマンド
```bash
npm run dev        # 既存プロセス停止 → 両方起動（推奨）
npm run dev:start  # 両方起動（停止せずに起動）
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
uv run python main.py
```
※ `npm run backend:only`は自動で`uv sync`を実行します

#### フロントエンドのみ
```bash
npm run frontend:only
# または
cd src/frontend
npm install
npm run dev
```

### 4. 便利なコマンド一覧

| コマンド | 説明 |
|---------|------|
| `npm run dev` | 🚀 フロントエンド + バックエンド同時起動 |
| `npm run backend:only` | バックエンドのみ起動 |
| `npm run frontend:only` | フロントエンドのみ起動 |

#### フロントエンド詳細コマンド
```bash
cd src/frontend
npm run build      # ビルド
npm run preview    # プレビュー
npm run lint       # ESLintチェック
```

#### バックエンド詳細コマンド
```bash
cd src/backend
uv run --frozen ruff format .    # コードフォーマット
uv run --frozen ruff check .     # リントチェック
uv run --frozen pyright          # 型チェック
```

## 🎯 使用方法

1. `npm run dev` でアプリケーションを起動
2. ブラウザで `http://localhost:5173` にアクセス
3. 左側のチャンネル一覧から好きなチャンネルを選択
4. メッセージを入力（**Shift+Enter**で送信、**Enter**で改行）
5. **🤖 AI機能**: メッセージに「@AI」を含めると、5つのAI人格（レン、ミナ、テツ、ルナ、ソラ）のいずれかが応答します
6. **🤖 AI自律会話**: 「雑談」チャンネルでは設定された間隔（デフォルト60秒）でAIたちが自動的に会話を継続します
7. メッセージはSupabase PostgreSQLデータベースに永続化されます

### AI機能の使用例

#### @AI メンション機能
```text
@AI こんにちは！
@AI プログラミングで困ってます
@AI 今日の天気はどう？
```

#### AI自律会話の設定（オプション）
```bash
# 環境変数設定（.env ファイルまたは直接設定）
export GEMINI_API_KEY="あなたのGemini APIキー"

# 🤖 AI自動会話機能の設定
export AI_CONVERSATION_INTERVAL_SECONDS=60   # 自動会話の間隔（秒単位、デフォルト: 60秒）
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
- **人格選択**: 既存の5つのAI人格（レン、ミナ、テツ、ルナ、ソラ）からランダム選択
- **@AI機能との共存**: 従来の@AIメンション機能も引き続き利用可能

## ✨ 実装済み機能

### フロントエンド
- [x] レスポンシブなチャンネル一覧
- [x] リアルタイムメッセージ表示
- [x] メッセージ入力・送信（Shift+Enter送信、Enter改行）
- [x] WebSocket通信
- [x] ダークモード対応

### バックエンド
- [x] REST API（チャンネル一覧、メッセージ履歴）
- [x] WebSocketによるリアルタイム通信
- [x] Supabase PostgreSQLデータベースによるメッセージ永続化
- [x] **Google Gemini AI統合**
- [x] **複数AI人格チャットボット（レン、ミナ、テツ、ルナ、ソラ）**
- [x] **@AI メンション機能**
- [x] **🤖 AI自律会話機能実装**（設定可能間隔・人間介入不要、最小1秒〜最大24時間）
- [x] **過去10件メッセージ履歴による文脈理解機能**
- [x] **AI連続発言防止機能**
- [x] **具体的で質の高いAI会話実現機能**
- [x] 堅牢な接続管理システム
- [x] チャンネル別メッセージ管理
- [x] CORS対応
- [x] **Supabase PostgreSQL移行完了**

## 🐛 最近の改善

### 2025-06-23: AI機能とデータベース改善
- **AI会話間隔設定改善**: `AI_CONVERSATION_INTERVAL_SECONDS`環境変数で秒単位での細かい調整が可能（最小1秒〜最大24時間）
- **user_type列追加**: メッセージテーブルにuser_type列を追加し、human/aiの識別を強化
- **データベーススキーマ更新**: Alembicマイグレーションによるスキーマアップデート

### 2025-06-22: AIメッセージ品質向上
- **AIメッセージ途切れ問題修正**: 最大出力トークン数を1000→2048に増加
- **AI連続発言防止機能**: 同じAI人格による連続発言を防止し、会話の多様性を確保
- **AI発言長調整**: 各AI人格に3-4文程度の適度な長さで応答するよう指示を追加
- **設定の柔軟性向上**: `AI_MAX_OUTPUT_TOKENS`環境変数でトークン数をカスタマイズ可能

## 🚧 今後の拡張予定

- [ ] ユーザー認証機能
- [ ] メッセージ検索機能
- [ ] ファイルアップロード機能
- [ ] 絵文字リアクション機能
- [ ] AI応答のカスタマイズ機能
- [ ] プッシュ通知機能
