# HOTFIX: messagesテーブルuser_typeカラム追加

## 問題

`npm run dev`実行時に以下のエラーが発生：

```
psycopg2.errors.UndefinedColumn: column messages.user_type does not exist
```

## 原因

- SQLAlchemyの`Message`モデルには`user_type`カラムが定義されている
- しかし、Supabaseデータベースの実際の`messages`テーブルには該当カラムが存在しない
- スキーマの不整合によりSQLクエリが失敗

## 修正内容

以下のSQL文を実行してカラムを追加：

```sql
ALTER TABLE messages 
ADD COLUMN user_type VARCHAR NOT NULL DEFAULT 'user';
```

## 実行日時

2025-06-22 実行完了

## 検証結果

- ✅ `npm run dev`が正常に起動
- ✅ フロントエンド: http://localhost:5173/ で動作確認
- ✅ バックエンド: http://0.0.0.0:8000 で動作確認  
- ✅ API `/api/channels/1/messages` でメッセージ取得成功
- ✅ WebSocket接続正常
- ✅ すべてのメッセージで`userType`フィールドが正常に返却

## 注意事項

今後のスキーマ変更時は、SQLAlchemyモデルとデータベーススキーマの同期を確実に行うこと。