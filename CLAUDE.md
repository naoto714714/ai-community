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
React + TypeScript + Mantineを使用したフロントエンドプロトタイプの開発プロジェクトで、
段階的な開発手順に従って機能を追加していく方式で進めています。

### 主要機能
- 複数チャンネルでのチャット機能
- リアルタイムメッセージ送受信（フロントエンドのみ）
- レスポンシブデザイン（PC版優先）
- ダークモード対応
- 自動返信機能（デバッグ用）

### 技術スタック
- **Frontend**: React 18.x + TypeScript 5.x + Mantine 7.x + Vite
- **Icons**: Tabler Icons
- **Date**: dayjs
- **Development**: ESLint + Prettier + pre-commit

## プロジェクト構成

```
ai-community/
├── docs/                      # ドキュメント
│   ├── chat-app-spec.md      # 仕様書
│   └── chat-app-guide.md     # 実装手順書
├── src/
│   ├── backend/              # バックエンド（将来実装予定）
│   └── frontend/             # フロントエンド
├── tests/                    # テスト（Python）
├── prompts/                  # プロンプトテンプレート
├── z/                        # 一時ファイル
├── CLAUDE.md                 # AI開発ガイドライン（このファイル）
├── README.md                 # プロジェクトREADME
├── .gitignore               # Git除外設定
├── .pre-commit-config.yaml  # pre-commit設定
├── pyproject.toml           # Python設定
└── uv.lock                  # UV依存関係ロック
```

## 起動方法

### 1. 前提条件
- Node.js 18.x以上
- npm

### 2. フロントエンド起動
```bash
# フロントエンドディレクトリに移動
cd src/frontend

# 依存関係インストール（初回のみ）
npm install

# 開発サーバー起動
npm run dev
```

ブラウザで `http://localhost:5173` にアクセス

### 3. その他のコマンド
```bash
# ビルド
npm run build

# プレビュー
npm run preview

# ESLintチェック
npm run lint
```

## 開発状況

### ✅ 完了済み
- [x] プロジェクト初期セットアップ
- [x] Vite + React + TypeScript環境構築
- [x] Mantine UIライブラリ導入
- [x] 基本設定・動作確認
- [x] 基本レイアウト構築（AppShell）

### 🚧 実装予定
- [ ] チャンネル一覧実装
- [ ] メッセージ入力欄実装
- [ ] メッセージ表示機能
- [ ] メッセージ送信・自動返信機能
- [ ] 最終調整とスタイリング

## デザイン仕様

- **レイアウト**: 左サイドバー（280px）+ メインエリア
- **カラーテーマ**: ダークモード対応（Mantineデフォルト）
- **アクセントカラー**: blue/violet系
- **フォント**: システムフォント（-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans JP'）
- **最小幅**: 1024px（PC版優先）

- Frontend開発ガイドライン: @docs/frontend-guideline.md
- Backend開発ガイドライン: @docs/backend-guideline.md
