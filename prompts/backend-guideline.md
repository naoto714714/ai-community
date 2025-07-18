# 開発ガイドライン

このドキュメントには、本コードベースでの作業に関する重要な情報が記載されています。これらのガイドラインに厳密に従ってください。

## コア開発ルール

1.  **パッケージ管理**
    -   `uv` のみを使用し、`pip` は絶対に使用しないでください。
    -   インストール: `uv add package`
    -   ツールの実行: `uv run tool`
    -   アップグレード: `uv add --dev package --upgrade-package package`
    -   **禁止事項**: `uv pip install`、`@latest` 構文

2.  **コード品質**
    -   全てのコードに型ヒントが必要です。
    -   パブリックAPIにはdocstringが必須です。
    -   関数は焦点を絞り、小さく保ってください。
    -   既存のパターンに厳密に従ってください。
    -   行の長さ: 最大120文字

3.  **テスト要件**
    -   フレームワーク: `uv run --frozen pytest`
    -   非同期テスト: `asyncio` ではなく `anyio` を使用してください。
    -   カバレッジ: エッジケースとエラーをテストしてください。
    -   新機能にはテストが必要です。
    -   バグ修正にはリグレッションテストが必要です。

## プルリクエスト

- 変更内容を詳細に記述したメッセージを作成してください。解決しようとしている問題の概要と、その解決方法に焦点を当ててください。明確さを加える場合を除き、コードの詳細には踏み込まないでください。

## コードフォーマット

1.  **Ruff**
    -   フォーマット: `uv run --frozen ruff format .`
    -   チェック: `uv run --frozen ruff check .`
    -   修正: `uv run --frozen ruff check . --fix`
    -   **重要な問題点**:
        -   行の長さ (120文字)
        -   インポートの並び替え (I001)
        -   未使用のインポート
    -   **行の折り返し**:
        -   文字列: 括弧を使用してください。
        -   関数呼び出し: 適切なインデントで複数行にしてください。
        -   インポート: 複数行に分割してください。

2.  **型チェック**
    -   ツール: `uv run --frozen pyright`
    -   **要件**:
        -   `Optional` に対する明示的な `None` チェック
        -   文字列の型の絞り込み
        -   チェックが通ればバージョン警告は無視可能です。

3.  **Pre-commit**
    -   設定: `.pre-commit-config.yaml`
    -   実行タイミング: `git commit` 時
    -   ツール: Prettier (YAML/JSON)、Ruff (Python)
    -   **Ruffの更新**:
        -   PyPiバージョンを確認してください。
        -   config revを更新してください。
        -   まず設定をコミットしてください。

## エラー解決

1.  **CI失敗**
    -   **修正順序**:
        1.  フォーマット
        2.  型エラー
        3.  リンティング
    -   **型エラー**:
        -   完全な行のコンテキストを取得してください。
        -   `Optional` 型をチェックしてください。
        -   型の絞り込みを追加してください。
        -   関数シグネチャを検証してください。

2.  **一般的な問題**
    -   **行の長さ**:
        -   括弧を使用して文字列を分割してください。
        -   関数呼び出しを複数行にしてください。
        -   インポートを分割してください。
    -   **型**:
        -   `None` チェックを追加してください。
        -   文字列型を絞り込んでください。
        -   既存のパターンに合わせてください。
    -   **Pytest**:
        -   テストが `anyio pytest` マークを見つけられない場合、`pytest` の実行コマンドの先頭に `PYTEST_DISABLE_PLUGIN_AUTOLOAD=""` を追加してみてください。
          例: `PYTEST_DISABLE_PLUGIN_AUTOLOAD="" uv run --frozen pytest`

3.  **ベストプラクティス**
    -   コミット前に `git status` をチェックしてください。
    -   型チェックの前にフォーマッターを実行してください。
    -   変更は最小限に留めてください。
    -   既存のパターンに従ってください。
    -   パブリックAPIを文書化してください。
    -   徹底的にテストしてください。
