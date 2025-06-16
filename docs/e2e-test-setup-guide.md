# E2Eテストセットアップガイド

## 概要

このガイドでは、AI CommunityプロジェクトでPlaywright MCPツールを使用してE2Eテストを実行するための環境構築と基本的な使用方法を説明します。

## 前提条件

- Node.js 18.x以上
- Python 3.11以上（バックエンド用）
- Claude Code CLIがインストール済み
- Playwright MCPが利用可能

## セットアップ手順

### 1. アプリケーションの起動

#### バックエンドの起動
```bash
cd src/backend
uv run uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### フロントエンドの起動
```bash
cd src/frontend
npm install  # 初回のみ
npm run dev
```

### 2. テスト環境の確認

以下のURLにアクセスして、アプリケーションが正常に動作することを確認：
- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8000/docs

## Playwright MCPツールの使用方法

### 基本的なコマンド

#### 1. ブラウザの起動とページ遷移
```
mcp__playwright__browser_navigate
- url: "http://localhost:5173"
```

#### 2. ページのスナップショット取得
```
mcp__playwright__browser_snapshot
```

#### 3. 要素のクリック
```
mcp__playwright__browser_click
- element: "チャンネル名"
- ref: "[要素の参照]"
```

#### 4. テキスト入力
```
mcp__playwright__browser_type
- element: "メッセージ入力欄"
- ref: "[要素の参照]"
- text: "テストメッセージ"
```

#### 5. スクリーンショット撮影
```
mcp__playwright__browser_take_screenshot
- filename: "test-result.png"
```

### テスト実行例

#### 基本的なメッセージ送信テスト

1. **アプリケーションを開く**
   ```
   browser_navigate(url="http://localhost:5173")
   ```

2. **初期表示を確認**
   ```
   browser_snapshot()
   # チャンネル一覧とチャットエリアが表示されることを確認
   ```

3. **メッセージを入力して送信**
   ```
   browser_type(
     element="メッセージ入力欄",
     ref="[input要素の参照]",
     text="こんにちは、テストメッセージです"
   )
   browser_press_key(key="Enter")
   ```

4. **送信結果を確認**
   ```
   browser_wait_for(text="こんにちは、テストメッセージです")
   browser_take_screenshot(filename="message-sent.png")
   ```

#### チャンネル切り替えテスト

1. **別のチャンネルをクリック**
   ```
   browser_click(
     element="#ゲーム チャンネル",
     ref="[チャンネル要素の参照]"
   )
   ```

2. **切り替え完了を待機**
   ```
   browser_wait_for(time=1)
   ```

3. **チャンネルが切り替わったことを確認**
   ```
   browser_snapshot()
   # アクティブチャンネルが変更されていることを確認
   ```

### マルチブラウザテスト

WebSocketのリアルタイム同期をテストする場合：

1. **新しいタブを開く**
   ```
   browser_tab_new(url="http://localhost:5173")
   ```

2. **最初のタブでメッセージ送信**
   ```
   browser_tab_select(index=0)
   browser_type(element="メッセージ入力欄", text="タブ1からのメッセージ")
   browser_press_key(key="Enter")
   ```

3. **2番目のタブで受信確認**
   ```
   browser_tab_select(index=1)
   browser_wait_for(text="タブ1からのメッセージ")
   ```

## トラブルシューティング

### よくある問題と解決方法

#### 1. WebSocket接続エラー
- バックエンドが起動していることを確認
- CORSの設定を確認
- ポート8000が他のプロセスで使用されていないか確認

#### 2. 要素が見つからない
- `browser_snapshot()`で現在のページ状態を確認
- 要素が読み込まれるまで`browser_wait_for()`で待機
- 正しい要素参照（ref）を使用しているか確認

#### 3. テストが不安定
- 適切な待機時間を設定（`browser_wait_for(time=秒数)`）
- ネットワークリクエストの完了を待つ
- 要素の表示を確認してから操作する

## ベストプラクティス

### 1. テストの独立性
- 各テストは独立して実行可能にする
- テスト前にデータをクリーンアップする
- テスト後に作成したデータを削除する

### 2. 待機戦略
- 固定時間の待機より、要素や条件の待機を優先
- `browser_wait_for(text="...")`を活用
- 非同期処理の完了を適切に待つ

### 3. アサーション
- スナップショットで視覚的に確認
- テキストの存在を確認
- エラーメッセージの不在を確認

### 4. デバッグ
- 各ステップでスクリーンショットを撮影
- コンソールメッセージを確認（`browser_console_messages()`）
- ネットワークリクエストを監視（`browser_network_requests()`）

## 継続的インテグレーション（CI）での実行

将来的にCIパイプラインでE2Eテストを実行する場合の推奨設定：

```yaml
# .github/workflows/e2e-test.yml の例
steps:
  - name: アプリケーション起動
    run: |
      # バックエンドとフロントエンドを起動
      
  - name: E2Eテスト実行
    run: |
      # Playwright MCPを使用したテスト実行
      
  - name: テスト結果の保存
    if: always()
    uses: actions/upload-artifact@v3
    with:
      name: test-results
      path: |
        *.png
        test-results/
```

## 次のステップ

1. 基本的なテストシナリオから始める
2. 徐々に複雑なシナリオを追加
3. エラーケースのテストを充実させる
4. パフォーマンステストを追加
5. アクセシビリティテストを実装

このガイドは、プロジェクトの進展とともに更新してください。