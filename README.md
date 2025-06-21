# AI Community

**AI チャットボット「ハルト」搭載**のモダンなリアルタイムチャットアプリケーション。フロントエンド（React）とバックエンド（FastAPI）のフルスタック構成で実装されています。

## 📋 プロジェクト概要

このプロジェクトは、React + TypeScript + Mantineを使用したフロントエンドと、FastAPI + SQLAlchemy + WebSocketを使用したバックエンドで構成されるチャットアプリケーションです。
リアルタイム通信・メッセージの永続化・AI チャットボット機能を実現しています。

### 主要機能

- 複数チャンネルでのチャット機能
- リアルタイムメッセージ送受信（WebSocket）
- メッセージの永続化（Supabase PostgreSQL）
- **🤖 AI チャットボット「ハルト」**（Google Gemini 2.5 Flash Preview 05-20）
- **@AI メンションでの AI 応答機能**
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

これでフロントエンドとバックエンドが同時に起動します！
（バックエンドの依存関係は自動で`uv sync`が実行されます）

- **フロントエンド**: `http://localhost:5173`
- **バックエンド**: `http://localhost:8000`

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
5. **🤖 AI機能**: メッセージに「@AI」を含めると、ハルトが応答します
6. メッセージはSupabase PostgreSQLデータベースに永続化されます

### AI機能の使用例
```text
@AI こんにちは！
@AI プログラミングで困ってます
@AI 今日の天気はどう？
```

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
- [x] **AI チャットボット「ハルト」**
- [x] **@AI メンション機能**
- [x] 堅牢な接続管理システム
- [x] チャンネル別メッセージ管理
- [x] CORS対応
- [x] **Supabase PostgreSQL移行完了**

## 🚧 今後の拡張予定

- [ ] ユーザー認証機能
- [ ] メッセージ検索機能
- [ ] ファイルアップロード機能
- [ ] 絵文字リアクション機能
- [ ] AI応答のカスタマイズ機能
- [ ] プッシュ通知機能
