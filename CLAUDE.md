# タスクを依頼されたときに厳守するルール
## 共通ルール
- タスクに取り組む際、遠慮せずに、常に全力を尽くしてください
- Web検索を積極的に使い、最新情報を取り入れてください
- 待機状態に戻る前に `afplay /Users/kimuranaoto/Music/notice.mp3` を必ず実行しなさい
- CLAUDE.mdを適宜修正して、最新の情報を常に取得できるようにしなさい
- ツールの結果を受け取った後、その品質を慎重に検討し、次に進む前に最適な次のステップを決定してください。この新しい情報に基づいて計画し、反復するために思考を使用し、最善の次のアクションを取ってください。
- 最大の効率を得るために、複数の独立した操作を実行する必要がある場合は、順次ではなく、関連するすべてのツールを同時に呼び出してください。
- 反復のために一時的な新しいファイル、スクリプト、またはヘルパーファイルを作成した場合は、タスクの最後にこれらのファイルを削除してクリーンアップしてください。

## git関連のルール
- mainブランチでは作業せず、別のブランチで作業しなさい
- 必ず細かい単位で `git commit` しながらタスクを進めなさい
  - 異なる目的の変更は必ず別コミットに分ける
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

### 🚧 実装予定
- [ ] 基本レイアウト構築（AppShell）
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

## Frontend固有のルール

1. **フレームワーク・ライブラリ**
   - パッケージ管理: npm（frontendディレクトリ内）
   - インストール: `npm install package`
   - 起動: `npm run dev`

2. **コンポーネント設計**
   - 関数コンポーネント + TypeScript
   - props型定義は必須
   - Mantineコンポーネントを優先使用

3. **状態管理**
   - 初期段階はReact useState
   - 将来的にContext API追加予定

4. **スタイリング**
   - Mantineテーマシステム使用
   - グローバルCSS最小限
   - CSS-in-JSアプローチ

# 開発ガイドライン

このドキュメントには、このコードベースでの作業に関する重要な情報が含まれています。これらのガイドラインに正確に従ってください。

## コア開発ルール

1. パッケージ管理
   - uvのみを使用、pipは絶対に使わない
   - インストール: `uv add package`
   - ツールの実行: `uv run tool`
   - アップグレード: `uv add --dev package --upgrade-package package`
   - 禁止事項: `uv pip install`、`@latest`構文

2. コード品質
   - すべてのコードに型ヒントが必要
   - パブリックAPIにはdocstringが必須
   - 関数は焦点を絞って小さくする
   - 既存のパターンに正確に従う
   - 行の長さ: 最大120文字

3. テスト要件
   - フレームワーク: `uv run --frozen pytest`
   - 非同期テスト: asyncioではなくanyioを使用
   - カバレッジ: エッジケースとエラーをテスト
   - 新機能にはテストが必要
   - バグ修正にはリグレッションテストが必要

## プルリクエスト

- 何が変更されたかの詳細なメッセージを作成する。解決しようとしている問題の高レベルな説明と、それがどのように解決されるかに焦点を当てる。明確さを加える場合を除き、コードの詳細には立ち入らない。

## Pythonツール

## コードフォーマット

1. Ruff
   - フォーマット: `uv run --frozen ruff format .`
   - チェック: `uv run --frozen ruff check .`
   - 修正: `uv run --frozen ruff check . --fix`
   - 重要な問題:
     - 行の長さ (120文字)
     - インポートの並び替え (I001)
     - 未使用のインポート
   - 行の折り返し:
     - 文字列: 括弧を使用
     - 関数呼び出し: 適切なインデントで複数行
     - インポート: 複数行に分割

2. 型チェック
   - ツール: `uv run --frozen pyright`
   - 要件:
     - Optionalに対する明示的なNoneチェック
     - 文字列の型の絞り込み
     - チェックが通ればバージョン警告は無視可能

3. Pre-commit
   - 設定: `.pre-commit-config.yaml`
   - 実行タイミング: git commit時
   - ツール: Prettier (YAML/JSON)、Ruff (Python)
   - Ruffの更新:
     - PyPiバージョンをチェック
     - config revを更新
     - まず設定をコミット

## エラー解決

1. CI失敗
   - 修正順序:
     1. フォーマット
     2. 型エラー
     3. リンティング
   - 型エラー:
     - 完全な行のコンテキストを取得
     - Optional型をチェック
     - 型の絞り込みを追加
     - 関数シグネチャを検証

2. 一般的な問題
   - 行の長さ:
     - 括弧で文字列を分割
     - 複数行の関数呼び出し
     - インポートを分割
   - 型:
     - Noneチェックを追加
     - 文字列型を絞り込む
     - 既存のパターンに合わせる
   - Pytest:
     - テストがanyio pytestマークを見つけられない場合、pytestの実行コマンドの先頭に PYTEST_DISABLE_PLUGIN_AUTOLOAD="" を追加してみる
       例: `PYTEST_DISABLE_PLUGIN_AUTOLOAD="" uv run --frozen pytest`

3. ベストプラクティス
   - コミット前にgit statusをチェック
   - 型チェック前にフォーマッターを実行
   - 変更は最小限に保つ
   - 既存のパターンに従う
   - パブリックAPIを文書化
   - 徹底的にテスト
