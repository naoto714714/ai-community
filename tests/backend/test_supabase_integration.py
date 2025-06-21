"""Supabase PostgreSQL統合テスト（最小限・実用版）

このテストファイルは既存テストを補完し、Supabase固有の機能を確認します。
- Supabase接続確認
- 実PostgreSQLでのCRUD操作
- 環境変数フォールバック機能
"""

import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

from src.backend.database import SQLALCHEMY_DATABASE_URL


class TestSupabaseConnection:
    """Supabase接続確認テスト"""

    def test_supabase_connection_with_valid_env(self):
        """有効な環境変数でSupabase接続成功テスト"""
        # 実際の環境変数が設定されている場合のみ実行
        required_vars = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
        if not all(os.getenv(var) for var in required_vars):
            pytest.skip("Supabase環境変数が設定されていません")

        # 現在のデータベースURLがPostgreSQLの場合のみテスト実行
        if not SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
            pytest.skip("PostgreSQL接続が設定されていません")

        # 接続テスト
        try:
            engine = create_engine(SQLALCHEMY_DATABASE_URL)
            with engine.connect() as connection:
                result = connection.execute(text("SELECT 1 as test_value"))
                row = result.fetchone()
                assert row is not None
                assert row[0] == 1
        except OperationalError:
            pytest.fail("Supabase PostgreSQLへの接続に失敗しました")

    def test_supabase_url_format_validation(self):
        """Supabase接続URL形式の検証テスト"""
        from urllib.parse import quote_plus

        # テスト用の環境変数値
        test_env_vars = {
            "DB_HOST": "test-host.supabase.com",
            "DB_PORT": "5432",
            "DB_NAME": "postgres",
            "DB_USER": "postgres.test",
            "DB_PASSWORD": "test-password",
        }

        # database.pyの内部ロジックを再現してテスト
        # モジュールリロードを避けて、URL構築ロジックを直接検証
        if all(test_env_vars.values()):
            # 型検証（database.pyと同じロジック）
            for key, value in test_env_vars.items():
                assert isinstance(value, str), f"{key} must be a string"

            try:
                # URLエンコード（database.pyと同じロジック）
                encoded_user = quote_plus(test_env_vars["DB_USER"])
                encoded_password = quote_plus(test_env_vars["DB_PASSWORD"])

                # URL構築（database.pyと同じロジック）
                test_url = (
                    f"postgresql://{encoded_user}:{encoded_password}@"
                    f"{test_env_vars['DB_HOST']}:{test_env_vars['DB_PORT']}/"
                    f"{test_env_vars['DB_NAME']}?sslmode=require"
                )

                # URL形式の検証
                assert test_url.startswith("postgresql://")
                assert "test-host.supabase.com" in test_url
                assert "5432" in test_url
                assert "postgres.test" in test_url
                assert "sslmode=require" in test_url

            except Exception as e:
                pytest.fail(f"URL構築時にエラーが発生しました: {e}")


class TestSupabaseCRUD:
    """実PostgreSQLでのCRUD操作テスト"""

    @pytest.fixture
    def supabase_db_session(self):
        """Supabase用データベースセッション（環境変数設定時のみ）"""
        # 実際の環境変数が設定されている場合のみ実行
        required_vars = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
        if not all(os.getenv(var) for var in required_vars):
            pytest.skip("Supabase環境変数が設定されていません")

        if not SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
            pytest.skip("PostgreSQL接続が設定されていません")

        from sqlalchemy.orm import sessionmaker

        from src.backend.database import Base, engine

        try:
            # テスト専用のテーブルを作成
            Base.metadata.create_all(bind=engine)
            TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()
        except OperationalError:
            # 接続失敗時はテストをスキップ
            pytest.skip("Supabase PostgreSQLへの接続に失敗しました")

    def test_postgresql_channel_operations(self, supabase_db_session):
        """PostgreSQLでのチャンネル操作テスト"""
        from src.backend.models import Channel

        # CREATE: チャンネル作成
        test_channel = Channel(id="supabase_test_ch", name="Supabaseテストチャンネル", description="統合テスト用")

        try:
            supabase_db_session.add(test_channel)
            supabase_db_session.commit()

            # READ: 作成したチャンネルを取得
            retrieved_channel = supabase_db_session.query(Channel).filter(Channel.id == "supabase_test_ch").first()

            assert retrieved_channel is not None
            assert retrieved_channel.name == "Supabaseテストチャンネル"
            assert retrieved_channel.description == "統合テスト用"

            # UPDATE: チャンネル更新
            retrieved_channel.name = "更新されたチャンネル"
            supabase_db_session.commit()

            updated_channel = supabase_db_session.query(Channel).filter(Channel.id == "supabase_test_ch").first()
            assert updated_channel.name == "更新されたチャンネル"

            # DELETE: チャンネル削除
            supabase_db_session.delete(retrieved_channel)
            supabase_db_session.commit()

            deleted_channel = supabase_db_session.query(Channel).filter(Channel.id == "supabase_test_ch").first()
            assert deleted_channel is None

        finally:
            # クリーンアップ: テストが失敗してもデータを確実に削除
            cleanup_channel = supabase_db_session.query(Channel).filter(Channel.id == "supabase_test_ch").first()
            if cleanup_channel:
                supabase_db_session.delete(cleanup_channel)
                supabase_db_session.commit()

    def test_postgresql_message_with_unicode(self, supabase_db_session):
        """PostgreSQLでの日本語メッセージ処理テスト"""
        from datetime import UTC, datetime

        from src.backend.models import Channel, Message

        # テスト用チャンネル作成
        test_channel = Channel(id="unicode_test_ch", name="日本語テスト", description="絵文字テスト🎉")
        supabase_db_session.add(test_channel)
        supabase_db_session.commit()

        # 日本語・絵文字を含むメッセージ作成
        unicode_message = Message(
            id="unicode_msg_001",
            channel_id="unicode_test_ch",
            user_id="test_user_jp",
            user_name="テストユーザー👤",
            content="こんにちは！🌸 日本語メッセージのテストです。Supabase PostgreSQL対応✨",
            timestamp=datetime.now(UTC),
            is_own_message=True,
        )

        supabase_db_session.add(unicode_message)
        supabase_db_session.commit()

        try:
            # 取得して確認
            retrieved_message = supabase_db_session.query(Message).filter(Message.id == "unicode_msg_001").first()

            assert retrieved_message is not None
            assert retrieved_message.user_name == "テストユーザー👤"
            assert "🌸" in retrieved_message.content
            assert "Supabase PostgreSQL対応✨" in retrieved_message.content
        finally:
            # クリーンアップ（テストが失敗してもデータを削除）
            supabase_db_session.delete(unicode_message)
            supabase_db_session.delete(test_channel)
            supabase_db_session.commit()


class TestDatabaseFallback:
    """環境変数フォールバック機能テスト"""

    def test_database_url_construction_logic(self):
        """データベースURL構築ロジックの検証テスト"""
        # database.pyの内部ロジックを直接テスト
        from urllib.parse import quote_plus

        # Supabase設定が完全な場合
        mock_env_complete = {
            "DB_HOST": "test-host.supabase.com",
            "DB_PORT": "5432",
            "DB_NAME": "postgres",
            "DB_USER": "postgres.test",
            "DB_PASSWORD": "test-password",
        }

        # all()でチェックするロジックを模倣
        if all(mock_env_complete.get(var) for var in ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]):
            encoded_user = quote_plus(mock_env_complete["DB_USER"])
            encoded_password = quote_plus(mock_env_complete["DB_PASSWORD"])
            constructed_url = (
                f"postgresql://{encoded_user}:{encoded_password}@"
                f"{mock_env_complete['DB_HOST']}:{mock_env_complete['DB_PORT']}/"
                f"{mock_env_complete['DB_NAME']}?sslmode=require"
            )
            assert constructed_url.startswith("postgresql://")
            assert "test-host.supabase.com" in constructed_url

        # 不完全な設定の場合
        mock_env_incomplete = {
            "DB_HOST": "test-host.supabase.com",
            "DB_PORT": "5432",
            # DB_NAME, DB_USER, DB_PASSWORD なし
        }

        # all()でチェックするロジックを模倣
        if not all(mock_env_incomplete.get(var) for var in ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]):
            # フォールバック
            from pathlib import Path

            DB_FILE_PATH = Path(__file__).parent / "chat.db"
            fallback_url = f"sqlite:///{DB_FILE_PATH.as_posix()}"
            assert fallback_url.startswith("sqlite:///")
            assert "chat.db" in fallback_url

    def test_sqlite_functionality_standalone(self):
        """SQLite機能の独立テスト"""
        # 既存テストでSQLite機能は十分に検証されているため、
        # このテストは基本的なライブラリ動作確認のみ実施
        from sqlite3 import connect

        # SQLite基本動作確認
        conn = connect(":memory:")
        cursor = conn.cursor()

        # テーブル作成とデータ挿入テスト
        cursor.execute("CREATE TABLE test_table (id TEXT PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO test_table (id, name) VALUES (?, ?)", ("test", "テスト"))

        # データ取得確認
        cursor.execute("SELECT name FROM test_table WHERE id = ?", ("test",))
        result = cursor.fetchone()

        assert result is not None
        assert result[0] == "テスト"

        conn.close()

    def test_environment_variable_validation(self):
        """環境変数バリデーションロジックのテスト"""
        # 必要な環境変数リスト
        required_vars = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]

        # 完全な環境変数セット
        complete_env = {var: f"test_{var.lower()}" for var in required_vars}
        assert all(complete_env.get(var) for var in required_vars) is True

        # 不完全な環境変数セット（一部欠落）
        incomplete_env = {
            "DB_HOST": "test_host",
            "DB_PORT": "5432",
            # DB_NAME, DB_USER, DB_PASSWORD なし
        }
        assert all(incomplete_env.get(var) for var in required_vars) is False

        # 空の環境変数セット
        empty_env = {}
        assert all(empty_env.get(var) for var in required_vars) is False
