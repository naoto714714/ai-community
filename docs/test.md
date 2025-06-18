# AI Community テストフレームワーク仕様書（実用版）

## 概要

AI Communityプロジェクトの**最小限かつ実用的な**テストフレームワーク仕様です。
過度な複雑さを避け、実際の開発で継続可能なテストを目標とします。

## 基本方針

### 現実的な目標
- **品質 > 完璧性**: 重要機能の確実な動作を優先
- **保守性 > 網羅性**: メンテナンスしやすいテストを重視
- **段階的導入**: 必要最小限から始めて徐々に拡張

### テストレベル
1. **コアテスト**: 最重要機能のテスト（必須）
2. **拡張テスト**: 追加機能のテスト（任意）

## 簡素なディレクトリ構成

```
ai-community/
├── tests/
│   ├── conftest.py              # pytest設定
│   ├── backend/                 # バックエンドテスト（3ファイル）
│   │   ├── test_models.py       # モデルテスト
│   │   ├── test_api.py          # API基本テスト
│   │   └── test_websocket.py    # WebSocket基本テスト
│   └── frontend/               # フロントエンドテスト（3ファイル）
│       ├── setup.ts            # Vitest設定
│       ├── components.test.tsx  # コンポーネントテスト
│       └── integration.test.tsx # 統合テスト
```

**総テスト数目標**: 約15個（バックエンド8個 + フロントエンド7個）

## バックエンドテスト（必要最小限）

### 1. test_models.py（3テスト）
```python
def test_channel_creation():
    """チャンネル作成テスト"""
    
def test_message_creation():
    """メッセージ作成テスト"""
    
def test_message_channel_relationship():
    """チャンネル-メッセージ関係テスト"""
```

### 2. test_api.py（3テスト）
```python
async def test_get_channels():
    """チャンネル一覧取得"""
    
async def test_get_messages():
    """メッセージ履歴取得"""
    
async def test_invalid_channel():
    """存在しないチャンネルのエラーハンドリング"""
```

### 3. test_websocket.py（2テスト）
```python
def test_websocket_connection():
    """WebSocket接続テスト"""
    
def test_websocket_message_send():
    """WebSocketメッセージ送信テスト"""
```

## フロントエンドテスト（必要最小限）

### 1. components.test.tsx（4テスト）
```typescript
// 主要コンポーネントのみ
describe('MessageItem', () => {
  it('メッセージが正しく表示される');
  it('自分のメッセージは右寄せで表示される');
});

describe('MessageInput', () => {
  it('テキスト入力が正常に動作する');
  it('Enterキーでメッセージが送信される');
});
```

### 2. integration.test.tsx（3テスト）
```typescript
describe('ChatApp Integration', () => {
  it('チャンネル切り替えでメッセージが更新される');
  it('WebSocket経由でメッセージが送受信される');
  it('エラー時に適切にハンドリングされる');
});
```

## テスト技術スタック

### バックエンド
- **pytest**: テストランナー
- **httpx**: 非同期HTTPクライアント
- **SQLite**: インメモリテスト用DB

### フロントエンド
- **Vitest**: テストランナー
- **React Testing Library**: コンポーネントテスト
- **MockWebSocket**: WebSocket モック

## 実装優先順位

### Phase 1: コアテスト（必須）
1. ✅ バックエンドモデルテスト（3個）
2. ✅ バックエンドAPIテスト（3個）
3. ⚠️ フロントエンドコンポーネントテスト（4個）

### Phase 2: 統合テスト（推奨）
4. ⚠️ WebSocketテスト（2個）
5. ⚠️ フロントエンド統合テスト（3個）

### Phase 3: 拡張テスト（任意）
- エラーハンドリング詳細テスト
- パフォーマンステスト
- エンドツーエンドテスト

## 品質指標

- **最低目標**: Phase 1完了（10テスト）
- **推奨目標**: Phase 2完了（15テスト）
- **カバレッジ**: 主要機能60%以上

## 削除対象

現在の過剰なテストファイルは段階的に削除：
- 詳細なユニットテスト → 統合テストに集約
- エッジケーステスト → 基本動作テストに集約
- 重複テスト → 最も重要なもの1つに絞る

## まとめ

**理念**: 「完璧よりも継続可能性」
- 15個のシンプルなテストで80%の価値を得る
- 残り20%の価値のために複雑にしない
- 実際の開発で使われ続けるテストを目指す