#!/usr/bin/env python3

import argparse
import json
import logging
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class LogMonitor:
    def __init__(self):
        self.log_patterns = {
            "websocket_connect": r"New WebSocket connection\. Total: (\d+)",
            "websocket_disconnect": r"WebSocket disconnected\. Total: (\d+)",
            "message_saved": r"Message saved: (.+)",
            "error": r"ERROR.*?Error.*?: (.+)",
            "warning": r"WARNING.*?: (.+)",
            "info": r"INFO.*?: (.+)",
        }

    def parse_log_line(self, line: str) -> dict[str, str] | None:
        """ログ行を解析してメタデータを抽出"""
        line = line.strip()
        if not line:
            return None

        # タイムスタンプを抽出（FastAPI/uvicornのログ形式）
        timestamp_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", line)
        timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"

        # ログレベルを抽出
        level = "INFO"  # デフォルト
        if "ERROR" in line:
            level = "ERROR"
        elif "WARNING" in line:
            level = "WARNING"
        elif "DEBUG" in line:
            level = "DEBUG"

        # パターンマッチング
        category = "general"
        details = ""

        for pattern_name, pattern in self.log_patterns.items():
            match = re.search(pattern, line)
            if match:
                category = pattern_name
                details = match.group(1) if match.groups() else ""
                break

        return {"timestamp": timestamp, "level": level, "category": category, "details": details, "raw_line": line}

    def analyze_logs(self, log_lines: list[str]) -> dict[str, Any]:
        """ログを分析して統計情報を生成"""
        parsed_logs = []
        for line in log_lines:
            parsed = self.parse_log_line(line)
            if parsed:
                parsed_logs.append(parsed)

        # 統計情報の計算
        total_lines = len(parsed_logs)
        levels = {}
        categories = {}
        errors = []
        websocket_connections = 0
        messages_saved = 0

        for log in parsed_logs:
            # レベル別カウント
            level = log["level"]
            levels[level] = levels.get(level, 0) + 1

            # カテゴリ別カウント
            category = log["category"]
            categories[category] = categories.get(category, 0) + 1

            # エラー収集
            if level == "ERROR":
                errors.append(log)

            # WebSocket接続数の追跡
            if category == "websocket_connect":
                try:
                    websocket_connections = int(log["details"])
                except ValueError:
                    pass

            # 保存されたメッセージ数
            if category == "message_saved":
                messages_saved += 1

        return {
            "total_lines": total_lines,
            "levels": levels,
            "categories": categories,
            "errors": errors,
            "websocket_connections": websocket_connections,
            "messages_saved": messages_saved,
            "analysis_time": datetime.now().isoformat(),
        }

    def print_analysis_report(self, analysis: dict[str, Any]):
        """分析結果のレポートを出力"""
        logger.info("=" * 60)
        logger.info("ログ分析レポート")
        logger.info("=" * 60)
        logger.info(f"分析時刻: {analysis['analysis_time']}")
        logger.info(f"総ログ行数: {analysis['total_lines']}")

        logger.info("\n--- ログレベル別統計 ---")
        for level, count in sorted(analysis["levels"].items()):
            logger.info(f"{level}: {count}")

        logger.info("\n--- カテゴリ別統計 ---")
        for category, count in sorted(analysis["categories"].items()):
            logger.info(f"{category}: {count}")

        logger.info("\n--- アプリケーション統計 ---")
        logger.info(f"WebSocket現在接続数: {analysis['websocket_connections']}")
        logger.info(f"保存されたメッセージ数: {analysis['messages_saved']}")

        # エラーがある場合は詳細表示
        if analysis["errors"]:
            logger.info(f"\n--- エラー詳細 ({len(analysis['errors'])}件) ---")
            for i, error in enumerate(analysis["errors"][-5:], 1):  # 最新5件のみ表示
                logger.info(f"{i}. [{error['timestamp']}] {error['details']}")
        else:
            logger.info("\n✅ エラーは検出されませんでした")

    def monitor_real_time(self, process_name: str = "python"):
        """リアルタイムログ監視"""
        logger.info(f"リアルタイムログ監視を開始します (プロセス: {process_name})")
        logger.info("Ctrl+C で終了")
        logger.info("-" * 60)

        try:
            # サーバープロセスのPIDを取得
            result = subprocess.run(["pgrep", "-f", "main.py"], capture_output=True, text=True)

            if result.returncode != 0:
                logger.error("バックエンドサーバーが見つかりません")
                logger.info("サーバーを起動してからもう一度実行してください:")
                logger.info("cd src/backend && uv run python main.py")
                return

            # ログをtailで監視（Macの場合はtailコマンドを使用）
            # 実際の運用では、ログファイルが存在する場合に監視
            logger.warning("リアルタイム監視機能は、ログファイル出力が設定されている場合に有効です")
            logger.info("現在は標準出力への出力のみのため、ここでは監視例を表示します")
            logger.info("")

            # デモンストレーション用のサンプルログ
            sample_logs = [
                "INFO:     Started server process [12345]",
                "INFO:     Waiting for application startup.",
                "INFO:     Application startup complete.",
                "INFO:     Uvicorn running on http://0.0.0.0:8000",
                "INFO:websocket:New WebSocket connection. Total: 1",
                "INFO:websocket:Message saved: test_12345",
                "INFO:websocket:WebSocket disconnected. Total: 0",
            ]

            logger.info("--- サンプルログ監視デモ ---")
            for log in sample_logs:
                parsed = self.parse_log_line(log)
                if parsed:
                    status = "🔴" if parsed["level"] == "ERROR" else "🟡" if parsed["level"] == "WARNING" else "🟢"
                    logger.info(
                        f"{status} [{parsed['level']}] {parsed['category']}: {parsed['details'] or parsed['raw_line']}"
                    )
                time.sleep(0.5)

        except KeyboardInterrupt:
            logger.info("\n\nログ監視を終了しました")

    def check_server_logs(self) -> list[str]:
        """サーバーログの取得を試行"""
        log_sources = [
            # 標準的なログファイルの場所を試行
            Path("app.log"),
            Path("backend.log"),
            Path("uvicorn.log"),
        ]

        logs = []

        for log_file in log_sources:
            if log_file.exists():
                try:
                    with open(log_file, encoding="utf-8") as f:
                        logs.extend(f.readlines())
                    logger.info(f"✅ ログファイル読み込み: {log_file}")
                except Exception as e:
                    logger.warning(f"ログファイル読み込みエラー {log_file}: {e}")

        if not logs:
            logger.info("ログファイルが見つかりません。サンプルログで動作確認します。")
            # サンプルログデータ
            logs = [
                "2025-06-16 10:00:00 INFO Started server process",
                "2025-06-16 10:00:01 INFO New WebSocket connection. Total: 1",
                "2025-06-16 10:00:05 INFO Message saved: test_msg_001",
                "2025-06-16 10:00:10 INFO WebSocket disconnected. Total: 0",
                "2025-06-16 10:01:00 WARNING Connection timeout detected",
                "2025-06-16 10:01:30 ERROR Database connection failed: timeout",
            ]

        return logs


def main():
    """メイン実行関数"""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    parser = argparse.ArgumentParser(description="AI Community Backend ログモニタリングツール")
    parser.add_argument(
        "--mode",
        choices=["analyze", "monitor"],
        default="analyze",
        help="実行モード: analyze=ログ分析, monitor=リアルタイム監視",
    )
    parser.add_argument("--output", help="分析結果の出力ファイル名（JSON形式）")

    args = parser.parse_args()

    monitor = LogMonitor()

    if args.mode == "monitor":
        monitor.monitor_real_time()
    else:
        # ログ分析モード
        logger.info("ログ分析を開始します...")
        logs = monitor.check_server_logs()
        analysis = monitor.analyze_logs(logs)
        monitor.print_analysis_report(analysis)

        # 結果をファイルに保存
        if args.output:
            output_file = Path(args.output)
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"\n📄 分析結果を {output_file} に保存しました")


if __name__ == "__main__":
    main()
