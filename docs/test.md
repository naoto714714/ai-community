# AI Community テストガイド

## 概要

AI Community プロジェクトのテストガイドです。
プロジェクト全体の品質方針や開発ワークフローについては、[CLAUDE.md](/CLAUDE.md) を参照してください。このドキュメントでは、具体的なテストの実装と実行方法に焦点を当てます。

## テスト構成

### ディレクトリ構成

```text
ai-community/
├── tests/
│   ├── conftest.py              # pytest 共通設定
│   ├── backend/                 # バックエンドテスト
│   │   ├── conftest.py          # バックエンド専用設定
│   │   ├── test_models.py       # DBモデルのテスト
│   │   ├── test_api.py          # REST API のテスト
│   │   └── test_websocket.py    # WebSocket通信とAI機能のテスト
│   └── frontend/                # フロントエンドテスト
│       ├── components.test.tsx  # UIコンポーネントの単体・結合テスト
│       └── integration.test.tsx # 複数コンポーネントを連携させた統合テスト
└── ...
```

### テストレベル

1.  **バックエンド**
    -   **単体テスト (`test_models.py`)**: SQLAlchemyモデルの属性やリレーションシップを検証します。
    -   **APIテスト (`test_api.py`)**: FastAPIのTestClientを使用し、各エンドポイントの正常系・異常系の応答を検証します。
    -   **WebSocketテスト (`test_websocket.py`)**: WebSocket接続、メッセージ送受信、AI応答生成（モック使用）をテストします。

2.  **フロントエンド**
    -   **コンポーネントテスト (`components.test.tsx`)**: `MessageItem` や `MessageInput` などのUIコンポーネントを個別にレンダリングし、Propsの受け渡しやイベントハンドリングを検証します。
    -   **統合テスト (`integration.test.tsx`)**: 複数のコンポーネント（`ChatArea`, `MessageList`など）を組み合わせて、ユーザーの一連の操作（メッセージ入力から表示まで）をシミュレートします。APIやWebSocket通信は `msw` を用いてモック化します。

## 技術スタック

### バックエンド (Python)

-   **テストランナー**: `pytest`
-   **非同期サポート**: `pytest-asyncio`
-   **HTTPクライアント**: `httpx` (FastAPI TestClient)
-   **モック**: `pytest-mock`
-   **DB**: テスト実行時は自動的にインメモリデータベース (SQLite) を使用

### フロントエンド (React + TypeScript)

-   **テストランナー**: `Vitest`
-   **コンポーネントテスト**: `@testing-library/react`
-   **ユーザー操作シミュレーション**: `@testing-library/user-event`
-   **DOMアサーション**: `@testing-library/jest-dom`
-   **ブラウザ環境**: `jsdom`
-   **API/WebSocketモック**: `msw` (Mock Service Worker)

## テスト実行

### バックエンド

ルートディレクトリで以下のコマンドを実行します。

```bash
# 全てのバックエンドテストを実行
uv run pytest tests/backend/
```

### フロントエンド

`src/frontend` ディレクトリに移動して実行します。

```bash
cd src/frontend

# 全てのフロントエンドテストを実行
npm test

# 開発中にテストを自動実行 (Watchモード)
npm run test:dev
```
