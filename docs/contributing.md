# コントリビューションガイド

## 概要

AI Community プロジェクトへのコントリビューションを歓迎します！
このガイドでは、開発環境のセットアップから、コード提出までの流れを説明します。

## 開発環境セットアップ

### 前提条件

- **Node.js**: 18.x 以上
- **Python**: 3.13 以上
- **uv**: `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Git**: 最新版推奨

### 初回セットアップ

```bash
# 1. リポジトリをフォーク・クローン
git clone <your-fork-url>
cd ai-community

# 2. pre-commit フックインストール
pip install pre-commit
pre-commit install

# 3. バックエンドセットアップ
cd src/backend
uv sync

# 4. フロントエンドセットアップ
cd src/frontend
npm install

# 5. 動作確認
# ターミナル1: バックエンド起動
cd src/backend && uv run python main.py

# ターミナル2: フロントエンド起動
cd src/frontend && npm run dev
```

## 開発ワークフロー

### ブランチ戦略

```bash
# main ブランチから新しいブランチを作成
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# または
git checkout -b fix/issue-description
git checkout -b docs/documentation-update
```

### 推奨ブランチ命名規則

- **機能追加**: `feature/add-user-authentication`
- **バグ修正**: `fix/websocket-connection-error`
- **ドキュメント**: `docs/api-documentation`
- **リファクタリング**: `refactor/simplify-message-handling`
- **テスト**: `test/add-integration-tests`

### コミットメッセージ規則

```bash
# 形式: <type>: <description>
# 
# type の種類:
# feat: 新機能
# fix: バグ修正
# docs: ドキュメント変更
# style: コードフォーマット
# refactor: リファクタリング
# test: テスト追加・修正
# chore: ビルド・設定変更

# 例:
git commit -m "feat: ユーザー認証機能を追加"
git commit -m "fix: WebSocket接続エラーを修正"
git commit -m "docs: API仕様書を更新"
```

### コード品質チェック

#### バックエンド

```bash
cd src/backend

# フォーマット
uv run --frozen ruff format .

# リント
uv run --frozen ruff check .

# 型チェック
uv run --frozen pyright

# テスト実行
uv run --frozen pytest
```

#### フロントエンド

```bash
cd src/frontend

# リント
npm run lint

# 型チェック
npx tsc --noEmit

# テスト実行（将来対応）
npm test
```

## コーディング規約

### Python（バックエンド）

#### 基本規則

- **行の長さ**: 最大120文字
- **型ヒント**: すべての関数・メソッドに必須
- **docstring**: パブリックAPI には必須
- **命名規則**: snake_case
- **インポート順序**: Ruff の設定に従う

#### 例: 関数定義

```python
def create_message(db: Session, message: MessageCreate) -> Message:
    """
    新しいメッセージをデータベースに作成します。
    
    Args:
        db: データベースセッション
        message: 作成するメッセージデータ
        
    Returns:
        作成されたメッセージオブジェクト
        
    Raises:
        ValueError: 無効なデータが提供された場合
        DatabaseError: データベース操作が失敗した場合
    """
    db_message = Message(
        id=message.id,
        channel_id=message.channel_id,
        user_id=message.user_id,
        user_name=message.user_name,
        content=message.content,
        timestamp=message.timestamp,
        is_own_message=message.is_own_message,
    )
    try:
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    except Exception:
        db.rollback()
        raise
```

#### エラーハンドリング

```python
# Good: 具体的な例外を捕捉
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise HTTPException(status_code=400, detail="Invalid input")
except DatabaseError as e:
    logger.error(f"Database error: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")

# Bad: 汎用的な例外捕捉
try:
    result = risky_operation()
except Exception:
    pass  # エラーを無視
```

### TypeScript（フロントエンド）

#### 基本規則

- **型定義**: すべての props・state に型定義
- **命名規則**: camelCase（関数・変数）、PascalCase（コンポーネント・型）
- **ファイル命名**: PascalCase（コンポーネント）、camelCase（ユーティリティ）
- **Export**: named export を推奨

#### 例: コンポーネント定義

```typescript
// types/chat.ts
export interface Message {
  id: string;
  channelId: string;
  userId: string;
  userName: string;
  content: string;
  timestamp: Date;
  isOwnMessage: boolean;
}

// components/MessageItem.tsx
interface MessageItemProps {
  message: Message;
  onEdit?: (messageId: string) => void;
  onDelete?: (messageId: string) => void;
}

export function MessageItem({ message, onEdit, onDelete }: MessageItemProps) {
  const handleEdit = useCallback(() => {
    onEdit?.(message.id);
  }, [message.id, onEdit]);
  
  return (
    <div className="message-item">
      <span className="user-name">{message.userName}</span>
      <p className="content">{message.content}</p>
      <time className="timestamp">
        {dayjs(message.timestamp).format('HH:mm')}
      </time>
    </div>
  );
}
```

#### フック使用

```typescript
// Custom Hook の例
function useWebSocket(url: string) {
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [connectionStatus, setConnectionStatus] = useState<'Connecting' | 'Open' | 'Closed'>('Connecting');
  
  useEffect(() => {
    const ws = new WebSocket(url);
    
    ws.onopen = () => setConnectionStatus('Open');
    ws.onclose = () => setConnectionStatus('Closed');
    
    setSocket(ws);
    
    return () => {
      ws.close();
    };
  }, [url]);
  
  return { socket, connectionStatus };
}
```

## テスト

### バックエンドテスト

#### ユニットテスト

```python
# tests/test_crud.py
import pytest
from sqlalchemy.orm import Session
from models import Message
from crud import create_message
from schemas import MessageCreate

def test_create_message(db_session: Session):
    """メッセージ作成のテスト"""
    message_data = MessageCreate(
        id="test_msg_1",
        channel_id="1",
        user_id="user_1",
        user_name="テストユーザー",
        content="テストメッセージ",
        timestamp=datetime.now(),
        is_own_message=True,
    )
    
    result = create_message(db_session, message_data)
    
    assert result.id == message_data.id
    assert result.content == message_data.content
    assert result.user_name == message_data.user_name
```

#### 統合テスト

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_get_channels():
    """チャンネル一覧取得のテスト"""
    response = client.get("/api/channels")
    assert response.status_code == 200
    
    channels = response.json()
    assert len(channels) > 0
    assert all("id" in channel and "name" in channel for channel in channels)
```

### フロントエンドテスト（将来対応）

#### コンポーネントテスト

```typescript
// components/__tests__/MessageItem.test.tsx
import { render, screen } from '@testing-library/react';
import { MessageItem } from '../MessageItem';
import type { Message } from '../../types/chat';

const mockMessage: Message = {
  id: '1',
  channelId: '1',
  userId: 'user1',
  userName: 'テストユーザー',
  content: 'テストメッセージ',
  timestamp: new Date('2024-01-01T12:00:00Z'),
  isOwnMessage: true,
};

test('renders message content', () => {
  render(<MessageItem message={mockMessage} />);
  
  expect(screen.getByText('テストユーザー')).toBeInTheDocument();
  expect(screen.getByText('テストメッセージ')).toBeInTheDocument();
  expect(screen.getByText('12:00')).toBeInTheDocument();
});
```

## プルリクエスト

### 提出前チェックリスト

- [ ] 新しい機能にはテストを追加
- [ ] バックエンドの型チェック・リントが通る
- [ ] フロントエンドのリントが通る
- [ ] 既存のテストがすべて通る
- [ ] ドキュメントを更新（必要に応じて）
- [ ] 変更内容を CHANGELOG.md に記載（重要な変更の場合）

### プルリクエストテンプレート

```markdown
## 概要
<!-- 何を変更したかを簡潔に説明 -->

## 変更内容
<!-- 詳細な変更内容 -->
- [ ] 機能追加
- [ ] バグ修正
- [ ] リファクタリング
- [ ] ドキュメント更新

## テスト
<!-- テスト方法・確認事項 -->
- [ ] ユニットテストを追加・更新
- [ ] 手動テストを実施
- [ ] 既存機能に影響がないことを確認

## スクリーンショット
<!-- UI変更の場合、before/after のスクリーンショット -->

## 関連Issue
<!-- 関連するIssue番号があれば記載 -->
Fixes #123

## 備考
<!-- その他特記事項 -->
```

## 問題報告

### Issue 作成時の情報

- **環境情報**: OS、Node.js バージョン、Python バージョン
- **再現手順**: 問題を再現するための具体的な手順
- **期待される動作**: 本来どのように動作すべきか
- **実際の動作**: 実際に起こった問題
- **ログ・エラーメッセージ**: 関連するエラー情報

### Issue テンプレート

```markdown
## 問題の概要
<!-- 問題を簡潔に説明 -->

## 環境情報
- OS: 
- Node.js: 
- Python: 
- Browser: 

## 再現手順
1. 
2. 
3. 

## 期待される動作
<!-- 本来の動作 -->

## 実際の動作
<!-- 問題のある動作 -->

## エラーログ
<!-- 関連するエラーメッセージ -->

## 追加情報
<!-- スクリーンショット等 -->
```

## リリースプロセス

### バージョニング

セマンティックバージョニング（SemVer）に従います:

- **MAJOR**: 互換性のない API 変更
- **MINOR**: 下位互換性のある機能追加
- **PATCH**: 下位互換性のあるバグ修正

### リリース手順

```bash
# 1. リリースブランチ作成
git checkout -b release/v1.1.0

# 2. バージョン更新
# package.json, pyproject.toml のバージョンを更新

# 3. CHANGELOG.md 更新
# 新しいバージョンの変更内容を記載

# 4. プルリクエスト作成・マージ

# 5. タグ作成
git tag v1.1.0
git push origin v1.1.0
```

## コミュニティ

### 質問・議論

- **GitHub Discussions**: 機能に関する議論
- **Issues**: バグ報告・機能リクエスト

### コミュニケーション

- 建設的で敬意を持った議論を心がける
- 技術的な根拠を示す
- 他の貢献者の意見を尊重する

## 参考資料

- [FastAPI 公式ドキュメント](https://fastapi.tiangolo.com/)
- [React 公式ドキュメント](https://react.dev/)
- [Mantine 公式ドキュメント](https://mantine.dev/)
- [SQLAlchemy 公式ドキュメント](https://docs.sqlalchemy.org/)
- [TypeScript ハンドブック](https://www.typescriptlang.org/docs/)

## ライセンス

このプロジェクトのライセンスについては [LICENSE](../LICENSE) ファイルを参照してください。