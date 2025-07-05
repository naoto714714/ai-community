# AI Community テストガイド

## 概要

AI Community プロジェクトの**実用的でメンテナンス可能な**テストガイドです。
Google Gemini AI統合チャットアプリケーションの品質を確保しつつ、開発効率を重視したテスト設計を採用しています。

## 基本方針

### 現実的な目標
- **品質 > 完璧性**: 重要機能の確実な動作を優先
- **保守性 > 網羅性**: メンテナンスしやすいテストを重視
- **段階的導入**: 必要最小限から始めて徐々に拡張
- **AI機能対応**: Google Gemini統合による複数AI人格チャットボットの応答品質とWebSocket通信の安定性を確保
- **AI自律会話対応**: 設定可能間隔（デフォルト60秒）での自動会話機能とAI連続発言防止機能のテスト
  - 境界値テスト（1秒・86400秒・範囲外値のバリデーション確認）

### テストレベル

1. **コアテスト**: 最重要機能のテスト（必須）

2. **AI機能テスト**: チャットボット・WebSocket通信テスト（推奨）

3. **拡張テスト**: 追加機能のテスト（任意）

## 簡素なディレクトリ構成

```text
ai-community/
├── tests/
│   ├── conftest.py              # pytest設定
│   ├── backend/                 # バックエンドテスト（5ファイル）
│   │   ├── conftest.py         # バックエンド専用設定
│   │   ├── test_models.py      # モデルテスト
│   │   ├── test_api.py         # REST API テスト
│   │   ├── test_websocket.py   # WebSocket + AI機能テスト
│   │   └── test_supabase_integration.py # Supabase統合テスト
│   └── frontend/               # フロントエンドテスト（1ファイル）
│       └── components.test.tsx  # 包括的コンポーネントテスト
├── src/
│   ├── backend/                # バックエンドソースコード
│   │   ├── main.py            # FastAPIアプリケーション
│   │   ├── models.py          # SQLAlchemyモデル
│   │   └── ...                # その他のバックエンドファイル
│   └── frontend/              # フロントエンドソースコード
│       ├── vitest.config.ts   # Vitestメイン設定
│       └── package.json       # テストスクリプト定義
└── pyproject.toml              # Pythonテスト設定
```

## テスト技術スタック

### バックエンド（Python 3.13）
- **pytest**: テストランナー・フィクスチャ管理
- **pytest-asyncio**: 非同期テスト対応
- **httpx**: 非同期HTTPクライアント（FastAPI テスト用）
- **pytest-mock**: モック機能（AI応答テスト用）
- **Supabase PostgreSQL**: 本番・開発データベース（統合テスト時）
- **PostgreSQL**: インメモリテスト用データベース（テスト専用）
- **anyio**: 非同期フレームワーク（uvと互換）

### フロントエンド（React 19 + TypeScript）
- **Vitest**: 高速テストランナー（Jest互換）
- **@testing-library/react**: Reactコンポーネントテスト
- **@testing-library/user-event**: ユーザーインタラクションテスト
- **@testing-library/jest-dom**: DOM assertion拡張
- **jsdom**: ブラウザ環境シミュレーション
- **msw**: WebSocket・API モック

## テスト実行方法

### バックエンドテスト
```bash
# 全テスト実行
cd src/backend && uv run --frozen pytest

# 特定テストファイル実行
uv run --frozen pytest tests/backend/test_models.py

# カバレッジ付き実行
uv run --frozen pytest --cov=src/backend
```

### フロントエンドテスト
```bash
# 全テスト実行
cd src/frontend && npm run test:run

# ウォッチモード
npm run test:dev

# カバレッジ付き実行
npm run test:coverage

# テストUI（ブラウザ表示）
npm run test:ui
```
