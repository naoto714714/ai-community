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
│       ├── public/           # 静的ファイル
│       ├── src/              # ソースコード
│       │   ├── assets/       # アセット
│       │   ├── components/   # Reactコンポーネント（将来追加）
│       │   ├── types/        # TypeScript型定義（将来追加）
│       │   ├── data/         # 初期データ（将来追加）
│       │   ├── App.tsx       # メインアプリケーション
│       │   ├── main.tsx      # エントリーポイント
│       │   └── index.css     # グローバルCSS
│       ├── package.json      # 依存関係
│       └── vite.config.ts    # Vite設定
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

## 🎯 開発状況

### ✅ 完了
- [x] プロジェクト初期セットアップ
- [x] Vite + React + TypeScript環境構築
- [x] Mantine UIライブラリ導入
- [x] 基本設定・動作確認

### 🚧 実装予定
- [ ] 基本レイアウト構築
- [ ] チャンネル一覧実装
- [ ] メッセージ入力欄実装
- [ ] メッセージ表示機能
- [ ] メッセージ送信・自動返信機能
- [ ] 最終調整とスタイリング

## 📖 開発ガイドライン

### コミット規則
- **細かい単位でコミット**：1つの論理的な変更 = 1コミット
- **コミットメッセージ形式**：`prefix: 日本語で説明`
  - `feat`: 新機能追加
  - `fix`: バグ修正
  - `refactor`: リファクタリング
  - `test`: テストの追加・修正
  - `docs`: ドキュメントの変更
  - `style`: コードフォーマットなど
  - `chore`: その他の変更

### ブランチ戦略
- mainブランチでは作業せず、別ブランチで作業
- 機能別にブランチを作成（例：`feat/chat-app-step1`）

## 🎨 デザイン仕様

- **カラーテーマ**: ダークモード対応（Mantineデフォルト）
- **アクセントカラー**: blue/violet系
- **フォント**: システムフォント（-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP'）
- **最小幅**: 1024px（PC版優先）

## 📚 参考ドキュメント

- [Mantine Documentation](https://mantine.dev/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)

## 🤝 コントリビューション

このプロジェクトはAI（Claude）との協働開発プロジェクトです。
開発ガイドラインに従って段階的に機能を実装していきます。
