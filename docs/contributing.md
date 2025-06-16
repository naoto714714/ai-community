# コントリビューションガイド

## 開発環境セットアップ

### 前提条件
- Node.js 18+ 
- Python 3.13+
- uv (`curl -LsSf https://astral.sh/uv/install.sh | sh`)

### セットアップ

```bash
# リポジトリクローン
git clone <your-fork-url>
cd ai-community

# Pre-commit インストール
pip install pre-commit
pre-commit install

# バックエンド
cd src/backend && uv sync

# フロントエンド
cd src/frontend && npm install
```

## 開発フロー

### ブランチ作成

```bash
git checkout -b feature/your-feature-name
# または
git checkout -b fix/bug-description
```

### コード品質チェック

**バックエンド**:
```bash
cd src/backend
uv run --frozen ruff format .  # フォーマット
uv run --frozen ruff check .   # リント
uv run --frozen pyright        # 型チェック
```

**フロントエンド**:
```bash
cd src/frontend
npm run lint  # ESLint
```

### コミット規則

```bash
# 形式: <type>: <description>
git commit -m "feat: 新機能を追加"
git commit -m "fix: バグを修正"
git commit -m "docs: ドキュメント更新"
```

## プルリクエスト

### 提出前チェックリスト
- [ ] 新機能にはテストを追加
- [ ] リント・型チェックが通る
- [ ] 既存機能に影響がない

### PR作成
```bash
git push origin your-branch-name
gh pr create --title "タイトル" --body "説明"
```

## 基本ルール

- **型安全性**: 全ての関数に型ヒント
- **小さなPR**: 1つの機能・修正につき1つのPR
- **テスト**: 新機能にはテストを追加
- **ドキュメント**: 重要な変更は文書化