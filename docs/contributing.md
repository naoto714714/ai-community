# AI Community コントリビューションガイド

**AI チャットボット「ハルト」搭載**のモダンなリアルタイムチャットアプリケーションへの貢献を歓迎します！

## 🚀 開発環境セットアップ

### 前提条件
- **Node.js**: 18.x以上
- **Python**: 3.13以上
- **uv**: Python パッケージマネージャー (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Git**: バージョン管理
- **Google Gemini API キー**: AI機能開発時（オプション）

### 🎯 一発セットアップ（推奨）

```bash
# 1. リポジトリクローン
git clone <your-fork-url>
cd ai-community

# 2. 依存関係インストール + 開発環境起動
npm install  # ルートの依存関係をインストール
npm run dev  # フロントエンド + バックエンド同時起動
```

### 📋 個別セットアップ

```bash
# Pre-commit フック設定
uv add --dev pre-commit
uv run pre-commit install

# バックエンド
cd src/backend && uv sync

# フロントエンド
cd src/frontend && npm install

# AI機能用（オプション）
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

## 🔄 開発フロー

### 1. ブランチ作成

```bash
# mainブランチから新しいブランチを作成
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
# または
git checkout -b fix/bug-description
git checkout -b docs/update-documentation
```

### 2. 開発・テスト

```bash
# 開発サーバー起動
npm run dev

# テスト実行
npm run test:backend    # バックエンドテスト
npm run test:frontend   # フロントエンドテスト
```

### 3. コード品質チェック

**🐍 バックエンド**:
```bash
cd src/backend
uv run --frozen ruff format .    # コードフォーマット
uv run --frozen ruff check .     # リント
uv run --frozen pyright          # 型チェック
uv run --frozen pytest           # テスト実行
```

**⚛️ フロントエンド**:
```bash
cd src/frontend
npm run format           # Prettier フォーマット
npm run lint:fix         # ESLint 自動修正
npm run type-check       # TypeScript 型チェック
npm run test:run         # テスト実行
```

### 4. コミット規則

```bash
# 形式: <type>: <description>（日本語OK）
git commit -m "feat: AI応答機能を追加"
git commit -m "fix: WebSocket接続エラーを修正"
git commit -m "docs: README.mdを更新"
git commit -m "test: メッセージ送信テストを追加"
git commit -m "refactor: コンポーネント構造を改善"
```

**コミット タイプ**:
- `feat`: 新機能
- `fix`: バグ修正
- `docs`: ドキュメント
- `test`: テスト
- `refactor`: リファクタリング
- `style`: スタイル・フォーマット
- `perf`: パフォーマンス改善

## 📋 プルリクエスト

### 提出前チェックリスト
- [ ] **テスト**: 新機能にはテストを追加
- [ ] **品質チェック**: Ruff、ESLint、型チェックが通る
- [ ] **既存機能**: 既存のテストが全て通る
- [ ] **ドキュメント**: 重要な変更は文書化
- [ ] **AI機能**: AI関連の変更はモックテストを追加

### PR作成・レビュー

```bash
# ブランチをプッシュ
git push origin your-branch-name

# GitHub CLI でPR作成
gh pr create --title "feat: 新機能の追加" --body "$(cat <<EOF
## 概要
この変更の概要を記載

## 変更内容
- 追加した機能
- 修正したバグ
- 更新したドキュメント

## テスト
- [ ] 新しいテストを追加
- [ ] 既存テストが通ることを確認

## 確認事項
- [ ] AI機能への影響確認済み
- [ ] レスポンシブ対応確認済み
EOF
)"
```

## 🔧 開発ルール・ベストプラクティス

### コード品質
- **型安全性**: 全ての関数に型ヒント（Python）・型定義（TypeScript）
- **小さなPR**: 1つの機能・修正につき1つのPR
- **テスト**: 新機能には必ずテストを追加
- **ドキュメント**: 重要な変更は文書化
- **AI機能**: 外部API依存はモックを使用

### 技術的ガイドライン
- **フロントエンド**: Mantineコンポーネント優先使用
- **バックエンド**: uvパッケージマネージャー必須使用
- **WebSocket**: リアルタイム通信の品質を重視
- **レスポンシブ**: モバイル対応を考慮
- **アクセシビリティ**: WAI-ARIA対応

## 🤖 AI機能開発時の注意点

### 開発環境
```bash
# 環境変数設定
export GEMINI_API_KEY="your_api_key"
# または .env ファイルに記載
echo "GEMINI_API_KEY=your_api_key" >> .env
```

### テスト戦略
- **モック使用**: Gemini API はモックでテスト
- **非同期対応**: AI応答の非同期性を考慮
- **エラーハンドリング**: API失敗時の適切な処理

### 人格・プロンプト編集
- **ハルトの人格**: `prompts/001_ハルト.md` で管理
- **応答品質**: フレンドリーで有用な応答を心がける
- **安全性**: 不適切な応答を避ける設計

## 📞 サポート・質問

- **Issue**: バグ報告・機能要望
- **Discussion**: 技術的な質問・アイデア共有
- **Discord**: リアルタイムな議論（準備中）

## 📄 関連ドキュメント

- [バックエンド仕様書](./backend.md)
- [フロントエンド開発ガイド](./frontend.md)
- [テストガイド](./test.md)
- [開発ガイドライン](../prompts/backend-guideline.md)
