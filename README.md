# AI Community

モダンでカジュアルなデザインのリアルタイムチャットアプリケーション。フロントエンドプロトタイプの開発プロジェクトです。

## 📋 プロジェクト概要

このプロジェクトは、React + TypeScript + Mantineを使用したチャットアプリケーションのフロントエンド実装です。
段階的な開発手順に従って機能を追加していく方式で進めています。

### 主要機能

- 複数チャンネルでのチャット機能
- リアルタイムメッセージ送受信（フロントエンドのみ）
- レスポンシブデザイン（PC版優先）
- ダークモード対応
- 自動返信機能（デバッグ用）

## 🛠 技術スタック

### フロントエンド
- **React**: 18.x
- **TypeScript**: 5.x
- **Mantine**: 7.x（UIコンポーネントライブラリ）
- **Mantine Hooks**: カスタムフック集
- **Tabler Icons**: アイコンライブラリ
- **Vite**: ビルドツール
- **dayjs**: 日付処理

### 開発環境
- **ESLint**: コード品質管理
- **Prettier**: コードフォーマット
- **pre-commit**: Gitフック管理

## 📁 プロジェクト構成

```
ai-community/
├── docs/                      # ドキュメント
│   ├── chat-app-spec.md      # 仕様書
│   └── chat-app-guide.md     # 実装手順書
├── src/
│   ├── backend/              # バックエンド（将来実装予定）
│   └── frontend/             # フロントエンド
├── CLAUDE.md                 # AI開発ガイドライン
├── .gitignore               # Git除外設定
├── .pre-commit-config.yaml  # pre-commit設定
└── README.md                # このファイル
```

## 🚀 セットアップ・起動方法

### 1. 前提条件

- Node.js 18.x以上
- npm

### 2. 依存関係のインストール

```bash
cd src/frontend
npm install
```

### 3. 開発サーバーの起動

```bash
npm run dev
```

ブラウザで `http://localhost:5173` にアクセスしてアプリケーションを確認できます。

### 4. ビルド

```bash
npm run build
```

### 5. プレビュー

```bash
npm run preview
```
