# AI Community テストガイド

## 概要

AI Community プロジェクトのテストに関するガイドです。
プロジェクト全体の品質方針や開発ワークフローについては、[CLAUDE.md](/CLAUDE.md) を参照してください。このドキュメントでは、具体的なテストの実装方法と実行方法に焦点を当てて説明します。

## テスト構成

### ディレクトリ構成

```text
ai-community/
├── tests/
│   ├── conftest.py              # pytestの共通設定ファイル
│   ├── backend/                 # バックエンドのテストコードを格納するディレクトリ
│   │   ├── conftest.py          # バックエンド専用のテスト設定ファイル
│   │   ├── test_models.py       # データベースモデルのテスト
│   │   ├── test_api.py          # REST APIのテスト
│   │   └── test_websocket.py    # WebSocket通信とAI機能のテスト
│   └── frontend/                # フロントエンドのテストコードを格納するディレクトリ
│       ├── components.test.tsx  # UIコンポーネントの単体テストおよび結合テスト
│       └── integration.test.tsx # 複数のコンポーネントを連携させた統合テスト
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
-   **データベース**: テスト実行時には、自動的にインメモリデータベース (SQLite) が使用されます。

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
# 全てのバックエンドテストを実行します
uv run pytest tests/backend/
```

### フロントエンド

`src/frontend` ディレクトリに移動して実行します。

```bash
cd src/frontend

# 全てのフロントエンドテストを実行します
npm test

# 開発中にテストを自動実行します (Watchモード)
npm run test:dev
```
