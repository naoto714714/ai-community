# Playwright E2Eテスト実装例

## 概要

このドキュメントでは、AI CommunityプロジェクトでPlaywright MCPツールを使用した具体的なE2Eテストの実装例を示します。

## 基本テストパターン

### 1. アプリケーション初期表示テスト

```
# アプリケーションにアクセス
browser_navigate(url="http://localhost:5173")

# 画面のスナップショットを取得
browser_snapshot()

# 期待値：
# - 左サイドバーにチャンネル一覧が表示される
# - メインエリアにチャットエリアが表示される
# - 「雑談」チャンネルがアクティブになっている

# スクリーンショットを保存
browser_take_screenshot(filename="initial-load.png")
```

### 2. メッセージ送信テスト

```
# メッセージ入力欄に文字を入力
browser_type(
  element="メッセージ入力欄",
  ref="textarea[placeholder='メッセージを入力...']",
  text="テストメッセージです"
)

# スクリーンショット（入力後）
browser_take_screenshot(filename="message-input.png")

# Enterキーでメッセージを送信
browser_press_key(key="Enter")

# メッセージが表示されるまで待機
browser_wait_for(text="テストメッセージです")

# 送信結果を確認
browser_take_screenshot(filename="message-sent.png")
```

### 3. チャンネル切り替えテスト

```
# 現在のチャンネルを確認
browser_snapshot()

# 「ゲーム」チャンネルをクリック
browser_click(
  element="#ゲーム チャンネル",
  ref="[data-channel-id='game']"
)

# 切り替えが完了するまで待機
browser_wait_for(time=1)

# チャンネル切り替え後のスナップショット
browser_snapshot()

# 期待値：
# - 「ゲーム」チャンネルがアクティブになっている
# - メッセージエリアが「ゲーム」チャンネルの内容に変わっている
```

## 複合テストシナリオ

### 4. マルチタブでのリアルタイム同期テスト

```
# 1つ目のタブ（既存）
browser_take_screenshot(filename="tab1-initial.png")

# 2つ目のタブを開く
browser_tab_new(url="http://localhost:5173")

# 2つ目のタブのスナップショット
browser_snapshot()

# 1つ目のタブに戻る
browser_tab_select(index=0)

# 1つ目のタブでメッセージを送信
browser_type(
  element="メッセージ入力欄",
  ref="textarea",
  text="タブ1からのメッセージ"
)
browser_press_key(key="Enter")

# 2つ目のタブに切り替え
browser_tab_select(index=1)

# 2つ目のタブでメッセージの受信を確認
browser_wait_for(text="タブ1からのメッセージ")
browser_take_screenshot(filename="tab2-received.png")

# 2つ目のタブから返信
browser_type(
  element="メッセージ入力欄",
  ref="textarea",
  text="タブ2からの返信"
)
browser_press_key(key="Enter")

# 1つ目のタブで返信を確認
browser_tab_select(index=0)
browser_wait_for(text="タブ2からの返信")
browser_take_screenshot(filename="tab1-reply-received.png")
```

### 5. 複数チャンネルでのメッセージ分離テスト

```
# チャンネル1（雑談）でメッセージ送信
browser_type(
  element="メッセージ入力欄",
  ref="textarea",
  text="雑談チャンネルのメッセージ"
)
browser_press_key(key="Enter")
browser_wait_for(text="雑談チャンネルのメッセージ")

# チャンネル2（ゲーム）に切り替え
browser_click(
  element="#ゲーム チャンネル",
  ref="[data-channel-id='game']"
)
browser_wait_for(time=1)

# チャンネル2でメッセージ送信
browser_type(
  element="メッセージ入力欄",
  ref="textarea",
  text="ゲームチャンネルのメッセージ"
)
browser_press_key(key="Enter")
browser_wait_for(text="ゲームチャンネルのメッセージ")

# チャンネル1に戻る
browser_click(
  element="#雑談 チャンネル",
  ref="[data-channel-id='general']"
)
browser_wait_for(time=1)

# チャンネル1のメッセージのみが表示されることを確認
browser_snapshot()
# 期待値：「雑談チャンネルのメッセージ」は表示される
# 「ゲームチャンネルのメッセージ」は表示されない
```

## エラーハンドリングテスト

### 6. バックエンド停止時のテスト

```
# 通常の接続状態を確認
browser_navigate(url="http://localhost:5173")
browser_wait_for(time=2)
browser_take_screenshot(filename="normal-connection.png")

# メッセージ送信を試行（この時点でバックエンドを手動停止）
browser_type(
  element="メッセージ入力欄",
  ref="textarea",
  text="接続エラーテスト"
)
browser_press_key(key="Enter")

# エラーメッセージまたは接続失敗の表示を待機
browser_wait_for(time=5)
browser_take_screenshot(filename="connection-error.png")

# コンソールエラーを確認
browser_console_messages()
```

### 7. 不正な入力のテスト

```
# XSS攻撃を試すスクリプトを入力
browser_type(
  element="メッセージ入力欄",
  ref="textarea",
  text="<script>alert('XSS')</script>"
)
browser_press_key(key="Enter")

# メッセージが文字列として表示されることを確認
browser_wait_for(text="<script>alert('XSS')</script>")
browser_take_screenshot(filename="xss-protection.png")

# 非常に長いメッセージのテスト
long_message = "あ" * 1001  # 1001文字
browser_type(
  element="メッセージ入力欄",
  ref="textarea",
  text=long_message
)
browser_press_key(key="Enter")

# 長すぎるメッセージが送信されないことを確認
browser_wait_for(time=2)
browser_take_screenshot(filename="long-message-test.png")
```

## パフォーマンステスト

### 8. 大量メッセージでのパフォーマンステスト

```
# 短時間で多数のメッセージを送信
for i in range(50):
    browser_type(
      element="メッセージ入力欄",
      ref="textarea",
      text=f"パフォーマンステスト メッセージ {i+1}"
    )
    browser_press_key(key="Enter")
    browser_wait_for(time=0.1)  # 短い待機時間

# 最終的な画面状態を確認
browser_wait_for(time=3)
browser_take_screenshot(filename="performance-test-result.png")

# スクロールが正常に動作することを確認
browser_press_key(key="Home")  # 画面上部にスクロール
browser_wait_for(time=1)
browser_take_screenshot(filename="scroll-top.png")

browser_press_key(key="End")   # 画面下部にスクロール
browser_wait_for(time=1)
browser_take_screenshot(filename="scroll-bottom.png")
```

## アクセシビリティテスト

### 9. キーボードナビゲーションテスト

```
# ページ読み込み
browser_navigate(url="http://localhost:5173")

# Tabキーでフォーカス移動
browser_press_key(key="Tab")
browser_take_screenshot(filename="focus-1.png")

browser_press_key(key="Tab")
browser_take_screenshot(filename="focus-2.png")

browser_press_key(key="Tab")
browser_take_screenshot(filename="focus-3.png")

# フォーカスがメッセージ入力欄に来たらメッセージを入力
browser_type(
  element="フォーカス中の要素",
  ref=":focus",
  text="キーボードナビゲーションテスト"
)
browser_press_key(key="Enter")

# メッセージが送信されることを確認
browser_wait_for(text="キーボードナビゲーションテスト")
browser_take_screenshot(filename="keyboard-navigation-success.png")
```

## テスト実行時の注意事項

### 事前準備
1. バックエンドサーバーが起動していること
2. フロントエンドサーバーが起動していること
3. データベースが初期化されていること

### テスト後のクリーンアップ
```
# 作成したメッセージをクリアする場合
# （実際のプロジェクトでは管理者機能やAPI経由で実行）

# 全てのタブを閉じる
browser_close()
```

### デバッグのヒント

1. **要素が見つからない場合**
   ```
   # 現在のページ構造を確認
   browser_snapshot()
   
   # 待機時間を増やす
   browser_wait_for(time=3)
   ```

2. **WebSocket接続の問題**
   ```
   # ネットワークリクエストを監視
   browser_network_requests()
   
   # コンソールメッセージを確認
   browser_console_messages()
   ```

3. **タイミングの問題**
   ```
   # 特定のテキストが表示されるまで待機
   browser_wait_for(text="期待するテキスト")
   
   # 特定のテキストが消えるまで待機
   browser_wait_for(textGone="読み込み中...")
   ```

## 継続的な改善

このテスト例は基本的なパターンを示しています。プロジェクトの成長に合わせて以下を追加してください：

- より複雑なユーザーシナリオ
- エッジケースの検証
- クロスブラウザテスト
- モバイル対応テスト（将来的に）
- パフォーマンス測定

各テストは独立して実行可能にし、テスト結果は適切に記録・管理することが重要です。