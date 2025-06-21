# AI Community テストガイド

## 概要

AI Community プロジェクトの**実用的でメンテナンス可能な**テストフレームワーク仕様です。
Google Gemini AI統合チャットアプリケーションの品質を確保しつつ、開発効率を重視したテスト設計を採用しています。

## 基本方針

### 現実的な目標
- **品質 > 完璧性**: 重要機能の確実な動作を優先
- **保守性 > 網羅性**: メンテナンスしやすいテストを重視
- **段階的導入**: 必要最小限から始めて徐々に拡張
- **AI機能対応**: チャットボット機能の品質確保

### テストレベル
1. **コアテスト**: 最重要機能のテスト（必須）
2. **AI機能テスト**: チャットボット・WebSocket通信テスト（推奨）
3. **拡張テスト**: 追加機能のテスト（任意）

## 簡素なディレクトリ構成

```text
ai-community/
├── tests/
│   ├── conftest.py              # pytest設定
│   ├── backend/                 # バックエンドテスト（4ファイル）
│   │   ├── conftest.py         # バックエンド専用設定
│   │   ├── test_models.py      # モデルテスト
│   │   ├── test_api.py         # REST API テスト
│   │   └── test_websocket.py   # WebSocket + AI機能テスト
│   └── frontend/               # フロントエンドテスト（3ファイル）
│       ├── setup.ts            # Vitest設定
│       ├── components.test.tsx  # コンポーネントテスト
│       └── integration.test.tsx # 統合テスト（AI応答含む）
├── src/frontend/
│   ├── vitest.config.ts        # Vitestメイン設定
│   └── package.json            # テストスクリプト定義
└── pyproject.toml              # Pythonテスト設定
```

**総テスト数目標**: 約18個（バックエンド10個 + フロントエンド8個）

## バックエンドテスト（Python + pytest）

### 1. test_models.py（3テスト）
```python
def test_channel_creation(test_db):
    """チャンネルモデルの作成テスト"""

def test_message_creation(test_db, seed_channels):
    """メッセージモデルの作成テスト"""

def test_message_channel_relationship(test_db, seed_channels):
    """チャンネル-メッセージ関係テスト"""
```

### 2. test_api.py（4テスト）
```python
async def test_get_channels(test_client):
    """チャンネル一覧取得 API テスト"""

async def test_get_messages(test_client, seed_data):
    """メッセージ履歴取得 API テスト"""

async def test_get_messages_with_pagination(test_client, seed_data):
    """ページネーション付きメッセージ取得テスト"""

async def test_invalid_channel(test_client):
    """存在しないチャンネルのエラーハンドリングテスト"""
```

### 3. test_websocket.py（3テスト）
```python
async def test_websocket_connection(test_client):
    """WebSocket接続テスト"""

async def test_websocket_message_send(test_client):
    """WebSocketメッセージ送信テスト"""

async def test_ai_response_trigger(test_client):
    """@AI メンション機能テスト（モック使用）"""
```

## フロントエンドテスト（TypeScript + Vitest + Testing Library）

### 1. components.test.tsx（5テスト）
```typescript
// 主要コンポーネントのユニットテスト
describe('MessageItem', () => {
  it('通常メッセージが正しく表示される');
  it('自分のメッセージは適切なスタイルで表示される');
  it('AI応答メッセージ（ハルト）が正しく表示される');
});

describe('MessageInput', () => {
  it('テキスト入力が正常に動作する');
  it('Shift+Enterでメッセージが送信される');
});
```

### 2. integration.test.tsx（3テスト）
```typescript
describe('ChatApp Integration', () => {
  it('チャンネル切り替えでメッセージが更新される');
  it('WebSocket経由でメッセージが送受信される');
  it('@AI メンション付きメッセージの送信とAI応答の受信');
});
```

## テスト技術スタック

### バックエンド（Python 3.13）
- **pytest**: テストランナー・フィクスチャ管理
- **pytest-asyncio**: 非同期テスト対応
- **httpx**: 非同期HTTPクライアント（FastAPI テスト用）
- **pytest-mock**: モック機能（AI応答テスト用）
- **SQLite**: インメモリテスト用データベース
- **anyio**: 非同期フレームワーク（uvと互換）

### フロントエンド（React 19 + TypeScript）
- **Vitest**: 高速テストランナー（Jest互換）
- **@testing-library/react**: Reactコンポーネントテスト
- **@testing-library/user-event**: ユーザーインタラクションテスト
- **@testing-library/jest-dom**: DOM assertion拡張
- **jsdom**: ブラウザ環境シミュレーション
- **msw**: WebSocket・API モック

## 実装状況・優先順位

### ✅ Phase 1: コアテスト（完了済み）
- [x] バックエンドモデルテスト（3個）
- [x] バックエンドAPIテスト（4個）
- [x] フロントエンドコンポーネントテスト（5個）

### ✅ Phase 2: 統合・AI機能テスト（完了済み）
- [x] WebSocket通信テスト（3個）
- [x] フロントエンド統合テスト（3個）
- [x] AI応答機能テスト（モック使用）

### 🚧 Phase 3: 拡張テスト（任意・将来予定）
- [ ] エラーハンドリング詳細テスト
- [ ] AI応答パフォーマンステスト
- [ ] E2Eテスト（Playwright使用予定）
- [ ] リアルタイム通信負荷テスト

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

## 品質指標・カバレッジ目標

- **現在達成**: 18テスト実装済み
- **カバレッジ目標**: 主要機能70%以上
- **AI機能テスト**: モック使用で基本動作確認済み
- **継続的統合**: pre-commitフックでテスト自動実行

## まとめ

**理念**: 「実用性重視の品質確保」
- 18個の戦略的テストで主要機能の品質を確保
- AI機能も含めた包括的なテストカバレッジ
- メンテナンス性を重視した継続可能なテスト設計
- 開発効率と品質のバランスを追求

## AI機能特有のテスト考慮事項

### モック戦略
- **Google Gemini API**: 外部依存を避けるためモック使用
- **WebSocket通信**: リアルタイム性を保ったテスト設計
- **非同期処理**: AI応答の非同期性を考慮したテスト

### 将来の拡張
- **実際のAI API**: 統合テスト環境での実API テスト
- **応答品質テスト**: AI応答内容の品質評価
- **パフォーマンステスト**: AI応答速度の監視
