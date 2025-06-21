#!/usr/bin/env python3

import argparse
import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class DatabaseInspector:
    def __init__(self, db_path: str = "chat.db"):
        self.db_path = Path(db_path)
        self.connection: sqlite3.Connection | None = None

    def connect(self) -> bool:
        """データベースに接続"""
        try:
            if not self.db_path.exists():
                logger.error(f"データベースファイルが見つかりません: {self.db_path}")
                return False

            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row  # 辞書形式でアクセス可能
            return True
        except Exception as e:
            logger.error(f"データベース接続エラー: {e}")
            return False

    def disconnect(self):
        """データベース接続を切断"""
        if self.connection:
            self.connection.close()
            self.connection = None

    def get_table_info(self, table_name: str) -> list[dict[str, Any]]:
        """テーブル情報を取得"""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()

            return [
                {
                    "cid": col["cid"],
                    "name": col["name"],
                    "type": col["type"],
                    "notnull": bool(col["notnull"]),
                    "default_value": col["dflt_value"],
                    "primary_key": bool(col["pk"]),
                }
                for col in columns
            ]
        except Exception as e:
            logger.warning(f"テーブル情報取得エラー {table_name}: {e}")
            return []

    def get_table_list(self) -> list[str]:
        """データベース内のテーブル一覧を取得"""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            return [row["name"] for row in cursor.fetchall()]
        except Exception as e:
            logger.warning(f"テーブル一覧取得エラー: {e}")
            return []

    def get_table_data(self, table_name: str, limit: int = 10) -> list[dict[str, Any]]:
        """テーブルデータを取得"""
        if not self.connection:
            return []

        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.warning(f"テーブルデータ取得エラー {table_name}: {e}")
            return []

    def get_table_count(self, table_name: str) -> int:
        """テーブルの行数を取得"""
        if not self.connection:
            return 0

        try:
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            return cursor.fetchone()[0]
        except Exception as e:
            logger.warning(f"テーブル行数取得エラー {table_name}: {e}")
            return 0

    def check_data_integrity(self) -> dict[str, Any]:
        """データ整合性をチェック"""
        if not self.connection:
            return {}

        results = {"checks": [], "errors": [], "warnings": []}

        try:
            cursor = self.connection.cursor()

            # 1. 必須テーブルの存在確認
            tables = self.get_table_list()
            required_tables = ["channels", "messages"]

            for table in required_tables:
                if table in tables:
                    results["checks"].append(f"✅ テーブル '{table}' が存在します")
                else:
                    results["errors"].append(f"❌ 必須テーブル '{table}' が見つかりません")

            # 2. 初期チャンネルの存在確認
            if "channels" in tables:
                cursor.execute("SELECT COUNT(*) FROM channels")
                channel_count = cursor.fetchone()[0]

                if channel_count >= 5:
                    results["checks"].append(f"✅ 初期チャンネル数: {channel_count}")
                else:
                    results["warnings"].append(f"⚠️ チャンネル数が少ない: {channel_count} (期待値: 5以上)")

                # 期待されるチャンネル名をチェック
                expected_channels = ["雑談", "ゲーム", "音楽", "趣味", "ニュース"]
                cursor.execute("SELECT name FROM channels")
                existing_channels = [row[0] for row in cursor.fetchall()]

                for expected in expected_channels:
                    if expected in existing_channels:
                        results["checks"].append(f"✅ チャンネル '{expected}' が存在します")
                    else:
                        results["warnings"].append(f"⚠️ 期待されるチャンネル '{expected}' が見つかりません")

            # 3. メッセージの整合性チェック
            if "messages" in tables:
                cursor.execute("SELECT COUNT(*) FROM messages")
                message_count = cursor.fetchone()[0]
                results["checks"].append(f"ℹ️ メッセージ総数: {message_count}")

                # 空のメッセージをチェック
                cursor.execute("SELECT COUNT(*) FROM messages WHERE content = '' OR content IS NULL")
                empty_messages = cursor.fetchone()[0]

                if empty_messages == 0:
                    results["checks"].append("✅ 空のメッセージはありません")
                else:
                    results["warnings"].append(f"⚠️ 空のメッセージ: {empty_messages}件")

                # 無効なチャンネルIDをチェック
                cursor.execute("""
                    SELECT COUNT(*) FROM messages
                    WHERE channel_id NOT IN (SELECT id FROM channels)
                """)
                invalid_channel_refs = cursor.fetchone()[0]

                if invalid_channel_refs == 0:
                    results["checks"].append("✅ 全メッセージが有効なチャンネルに所属しています")
                else:
                    results["errors"].append(f"❌ 無効なチャンネル参照: {invalid_channel_refs}件")

            # 4. タイムスタンプの妥当性チェック
            if "messages" in tables:
                cursor.execute("""
                    SELECT COUNT(*) FROM messages
                    WHERE timestamp > datetime('now', '+1 day')
                """)
                future_messages = cursor.fetchone()[0]

                if future_messages == 0:
                    results["checks"].append("✅ 未来のタイムスタンプはありません")
                else:
                    results["warnings"].append(f"⚠️ 未来のタイムスタンプ: {future_messages}件")

        except Exception as e:
            results["errors"].append(f"❌ 整合性チェック中にエラー: {e}")

        return results

    def get_statistics(self) -> dict[str, Any]:
        """データベース統計情報を取得"""
        if not self.connection:
            return {}

        stats = {
            "database_file": str(self.db_path),
            "file_size": self.db_path.stat().st_size if self.db_path.exists() else 0,
            "tables": {},
            "generated_at": datetime.now().isoformat(),
        }

        try:
            cursor = self.connection.cursor()
            tables = self.get_table_list()

            for table in tables:
                table_stats = {
                    "row_count": self.get_table_count(table),
                    "columns": self.get_table_info(table),
                    "sample_data": self.get_table_data(table, 3),
                }
                stats["tables"][table] = table_stats

            # 追加統計情報
            if "messages" in tables:
                # チャンネル別メッセージ数
                cursor.execute("""
                    SELECT c.name, COUNT(m.id) as message_count
                    FROM channels c
                    LEFT JOIN messages m ON c.id = m.channel_id
                    GROUP BY c.id, c.name
                    ORDER BY message_count DESC
                """)
                stats["messages_by_channel"] = [{"channel": row[0], "count": row[1]} for row in cursor.fetchall()]

                # 最新メッセージ
                cursor.execute("""
                    SELECT user_name, content, timestamp
                    FROM messages
                    ORDER BY created_at DESC
                    LIMIT 5
                """)
                stats["recent_messages"] = [
                    {
                        "user": row[0],
                        "content": row[1][:50] + "..." if len(row[1]) > 50 else row[1],
                        "timestamp": row[2],
                    }
                    for row in cursor.fetchall()
                ]

        except Exception as e:
            stats["error"] = str(e)

        return stats

    def print_schema_report(self):
        """データベーススキーマレポートを出力"""
        logger.info("=" * 60)
        logger.info("データベーススキーマレポート")
        logger.info("=" * 60)
        logger.info(f"データベースファイル: {self.db_path}")

        if self.db_path.exists():
            file_size = self.db_path.stat().st_size
            logger.info(f"ファイルサイズ: {file_size:,} バイト")

        tables = self.get_table_list()
        logger.info(f"テーブル数: {len(tables)}")

        for table in tables:
            logger.info(f"\n--- テーブル: {table} ---")
            columns = self.get_table_info(table)
            row_count = self.get_table_count(table)
            logger.info(f"行数: {row_count}")
            logger.info("カラム:")

            for col in columns:
                pk_mark = " (PK)" if col["primary_key"] else ""
                null_mark = " NOT NULL" if col["notnull"] else ""
                default_mark = f" DEFAULT {col['default_value']}" if col["default_value"] else ""
                logger.info(f"  - {col['name']}: {col['type']}{pk_mark}{null_mark}{default_mark}")

    def print_data_report(self, limit: int = 5):
        """データベースデータレポートを出力"""
        logger.info("\n" + "=" * 60)
        logger.info("データベースデータレポート")
        logger.info("=" * 60)

        tables = self.get_table_list()

        for table in tables:
            logger.info(f"\n--- テーブル: {table} ---")
            data = self.get_table_data(table, limit)

            if data:
                logger.info(f"データ例 (最新{min(len(data), limit)}件):")
                for i, row in enumerate(data, 1):
                    logger.info(f"  {i}. {dict(row)}")
            else:
                logger.info("  データがありません")

    def print_integrity_report(self):
        """データ整合性レポートを出力"""
        logger.info("\n" + "=" * 60)
        logger.info("データ整合性レポート")
        logger.info("=" * 60)

        integrity = self.check_data_integrity()

        if integrity["checks"]:
            logger.info("✅ 正常チェック:")
            for check in integrity["checks"]:
                logger.info(f"  {check}")

        if integrity["warnings"]:
            logger.info("\n⚠️ 警告:")
            for warning in integrity["warnings"]:
                logger.info(f"  {warning}")

        if integrity["errors"]:
            logger.info("\n❌ エラー:")
            for error in integrity["errors"]:
                logger.info(f"  {error}")

        if not integrity["errors"]:
            logger.info("\n🎉 データベースの整合性に問題はありません")


def main():
    """メイン実行関数"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="AI Community Backend データベース検査ツール")
    parser.add_argument("--db", default="chat.db", help="データベースファイルパス")
    parser.add_argument("--output", help="統計情報の出力ファイル名（JSON形式）")
    parser.add_argument("--limit", type=int, default=5, help="データ表示件数の制限")
    parser.add_argument("--schema-only", action="store_true", help="スキーマ情報のみ表示")

    args = parser.parse_args()

    inspector = DatabaseInspector(args.db)

    if not inspector.connect():
        sys.exit(1)

    try:
        # スキーマレポート
        inspector.print_schema_report()

        if not args.schema_only:
            # データレポート
            inspector.print_data_report(args.limit)

            # 整合性レポート
            inspector.print_integrity_report()

        # 統計情報をファイルに出力
        if args.output:
            stats = inspector.get_statistics()
            output_file = Path(args.output)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"\n📄 統計情報を {output_file} に保存しました")

    finally:
        inspector.disconnect()


if __name__ == "__main__":
    main()
