#!/usr/bin/env python3
"""
AI Community Backend - 総合テストスクリプト
ステップ7: 最終確認とテスト

このスクリプトは以下のテストを実行します:
1. チャンネル一覧取得テスト
2. WebSocketメッセージ送信テスト
3. メッセージ履歴取得テスト
4. データベース内容確認
5. ログ出力確認
"""

import asyncio
import json
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import websockets


class BackendTester:
    def __init__(self, base_url: str = "http://localhost:8000", ws_url: str = "ws://localhost:8000/ws"):
        self.base_url = base_url
        self.ws_url = ws_url
        self.db_path = Path("chat.db")
        self.test_results: list[dict[str, Any]] = []

    def log_test_result(self, test_name: str, success: bool, message: str = "", data: Any = None):
        """テスト結果をログに記録"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }
        self.test_results.append(result)

        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {message}")
        if data and not success:
            print(f"   Data: {data}")

    def test_server_connectivity(self) -> bool:
        """サーバー接続テスト"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            success = response.status_code == 200
            data = response.json() if success else None
            self.log_test_result("Server Connectivity", success, f"Status: {response.status_code}", data)
            return success
        except Exception as e:
            self.log_test_result("Server Connectivity", False, f"Connection failed: {str(e)}")
            return False

    def test_channels_api(self) -> bool:
        """チャンネル一覧取得APIテスト"""
        try:
            response = requests.get(f"{self.base_url}/api/channels", timeout=10)
            success = response.status_code == 200

            if success:
                channels = response.json()
                expected_channels = ["雑談", "ゲーム", "音楽", "趣味", "ニュース"]
                channel_names = [ch["name"] for ch in channels]

                success = all(name in channel_names for name in expected_channels)
                message = f"Found {len(channels)} channels" if success else "Missing expected channels"
            else:
                channels = None
                message = f"HTTP {response.status_code}"

            self.log_test_result("Channels API", success, message, channels)
            return success
        except Exception as e:
            self.log_test_result("Channels API", False, f"Request failed: {str(e)}")
            return False

    async def test_websocket_messaging(self) -> bool:
        """WebSocketメッセージ送信テスト"""
        try:
            async with websockets.connect(self.ws_url) as websocket:
                # テストメッセージを送信
                test_message = {
                    "type": "message:send",
                    "data": {
                        "id": f"test_comprehensive_{int(datetime.now().timestamp())}",
                        "channel_id": "1",
                        "user_id": "test_user",
                        "user_name": "総合テストユーザー",
                        "content": "総合テスト用メッセージ",
                        "timestamp": datetime.now().isoformat() + "Z",
                        "is_own_message": True,
                    },
                }

                await websocket.send(json.dumps(test_message))

                # レスポンスを待機（タイムアウト付き）
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                response_data = json.loads(response)

                success = (
                    response_data.get("type") == "message:saved"
                    and response_data.get("data", {}).get("success") is True
                )

                message = "Message sent and saved successfully" if success else "Failed to save message"
                self.log_test_result("WebSocket Messaging", success, message, response_data)
                return success

        except Exception as e:
            self.log_test_result("WebSocket Messaging", False, f"WebSocket test failed: {str(e)}")
            return False

    def test_messages_api(self) -> bool:
        """メッセージ履歴取得APIテスト"""
        try:
            # チャンネル1のメッセージを取得
            response = requests.get(f"{self.base_url}/api/channels/1/messages?limit=10", timeout=10)
            success = response.status_code == 200

            if success:
                data = response.json()
                messages = data.get("messages", [])
                total = data.get("total", 0)

                message = f"Retrieved {len(messages)} messages (total: {total})"
            else:
                data = None
                message = f"HTTP {response.status_code}"

            self.log_test_result("Messages API", success, message, data)
            return success
        except Exception as e:
            self.log_test_result("Messages API", False, f"Request failed: {str(e)}")
            return False

    def test_database_content(self) -> bool:
        """データベース内容確認テスト"""
        try:
            if not self.db_path.exists():
                self.log_test_result("Database Content", False, "Database file not found")
                return False

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # テーブル存在確認
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]

            required_tables = ["channels", "messages"]
            missing_tables = [t for t in required_tables if t not in tables]

            if missing_tables:
                conn.close()
                self.log_test_result("Database Content", False, f"Missing tables: {missing_tables}")
                return False

            # チャンネル数確認
            cursor.execute("SELECT COUNT(*) FROM channels")
            channel_count = cursor.fetchone()[0]

            # メッセージ数確認
            cursor.execute("SELECT COUNT(*) FROM messages")
            message_count = cursor.fetchone()[0]

            conn.close()

            success = channel_count >= 5  # 初期チャンネル数
            message = f"Channels: {channel_count}, Messages: {message_count}"

            self.log_test_result("Database Content", success, message)
            return success

        except Exception as e:
            self.log_test_result("Database Content", False, f"Database check failed: {str(e)}")
            return False

    def check_server_process(self) -> bool:
        """サーバープロセス確認"""
        try:
            # ポート8000が使用されているか確認
            result = subprocess.run(["lsof", "-i", ":8000"], capture_output=True, text=True, timeout=5)

            server_running = result.returncode == 0 and "python" in result.stdout.lower()
            message = "Backend server is running" if server_running else "Backend server not detected"

            self.log_test_result("Server Process", server_running, message)
            return server_running
        except Exception as e:
            self.log_test_result("Server Process", False, f"Process check failed: {str(e)}")
            return False

    async def run_all_tests(self) -> dict[str, Any]:
        """全テストを実行"""
        print("=" * 60)
        print("AI Community Backend - 総合テスト開始")
        print("=" * 60)

        start_time = datetime.now()

        # テスト実行順序
        tests = [
            ("Server Process Check", self.check_server_process),
            ("Server Connectivity", self.test_server_connectivity),
            ("Channels API", self.test_channels_api),
            ("WebSocket Messaging", self.test_websocket_messaging),
            ("Messages API", self.test_messages_api),
            ("Database Content", self.test_database_content),
        ]

        passed = 0
        failed = 0

        for test_name, test_func in tests:
            print(f"\n--- {test_name} ---")
            try:
                if asyncio.iscoroutinefunction(test_func):
                    result = await test_func()
                else:
                    result = test_func()

                if result:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                print(f"❌ ERROR {test_name}: {str(e)}")
                failed += 1

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # 結果サマリー
        print("\n" + "=" * 60)
        print("テスト結果サマリー")
        print("=" * 60)
        print(f"実行時間: {duration:.2f}秒")
        print(f"成功: {passed}")
        print(f"失敗: {failed}")
        print(f"成功率: {(passed / (passed + failed) * 100):.1f}%" if (passed + failed) > 0 else "0.0%")

        overall_success = failed == 0
        status = "✅ 全テスト合格" if overall_success else f"❌ {failed}個のテストが失敗"
        print(f"\n{status}")

        return {
            "overall_success": overall_success,
            "passed": passed,
            "failed": failed,
            "duration": duration,
            "test_results": self.test_results,
        }


def main():
    """メイン実行関数"""
    print("AI Community Backend 総合テストツール")
    print("注意: バックエンドサーバーが起動している必要があります")
    print("起動コマンド: cd src/backend && uv run python main.py")
    print()

    # 確認プロンプト
    response = input("テストを開始しますか？ (y/N): ").strip().lower()
    if response != "y":
        print("テストをキャンセルしました。")
        return

    tester = BackendTester()

    try:
        result = asyncio.run(tester.run_all_tests())

        # 結果をファイルに保存
        result_file = Path("test_results.json")
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n詳細な結果は {result_file} に保存されました。")

        # 終了コード
        sys.exit(0 if result["overall_success"] else 1)

    except KeyboardInterrupt:
        print("\n\nテストが中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n予期しないエラー: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
