#!/usr/bin/env python3
"""
AI Community Backend - ステップ7総合実行スクリプト
ステップ7: 最終確認とテスト

このスクリプトは以下の処理を順次実行します:
1. 総合テスト実行
2. ログ分析
3. データベース検査
4. 総合レポート生成
"""

import asyncio
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


class Step7TestRunner:
    def __init__(self):
        self.start_time = datetime.now()
        self.results = {
            "test_execution": {},
            "log_analysis": {},
            "database_inspection": {},
            "overall_status": "pending",
        }
        self.backend_dir = Path(__file__).parent

    def check_dependencies(self) -> bool:
        """依存関係とファイルの存在確認"""
        print("=" * 60)
        print("ステップ7: 事前チェック")
        print("=" * 60)

        required_files = ["test_comprehensive.py", "log_monitor.py", "db_inspector.py", "main.py"]

        missing_files = []
        for file in required_files:
            file_path = self.backend_dir / file
            if file_path.exists():
                print(f"✅ {file}")
            else:
                print(f"❌ {file} が見つかりません")
                missing_files.append(file)

        # 依存関係チェック
        print("\n--- 依存関係チェック ---")
        try:
            __import__("requests")
            print("✅ requests")
        except ImportError:
            print("❌ requests が見つかりません")
            missing_files.append("requests")

        try:
            __import__("websockets")
            print("✅ websockets")
        except ImportError:
            print("❌ websockets が見つかりません")
            missing_files.append("websockets")

        if missing_files:
            print(f"\n❌ 不足している依存関係: {', '.join(missing_files)}")
            print("必要な依存関係をインストールしてください:")
            print("uv add requests websockets")
            return False

        print("\n✅ 全ての依存関係が確認できました")
        return True

    def check_server_status(self) -> bool:
        """サーバーが起動しているかチェック"""
        print("\n--- サーバー起動状況チェック ---")
        try:
            result = subprocess.run(["lsof", "-i", ":8000"], capture_output=True, text=True, timeout=5)

            if result.returncode == 0 and "python" in result.stdout.lower():
                print("✅ バックエンドサーバーが起動中です")
                return True
            else:
                print("❌ バックエンドサーバーが起動していません")
                print("サーバーを起動してください:")
                print("cd src/backend && uv run python main.py")
                return False

        except Exception as e:
            print(f"⚠️ サーバー状況チェックエラー: {e}")
            return False

    async def run_comprehensive_tests(self) -> bool:
        """総合テストの実行"""
        print("\n" + "=" * 60)
        print("ステップ7-1: 総合テスト実行")
        print("=" * 60)

        try:
            # test_comprehensive.pyを実行
            process = await asyncio.create_subprocess_exec(
                sys.executable,
                "test_comprehensive.py",
                cwd=self.backend_dir,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
            )

            # 自動的に "y" を入力してテストを開始
            stdout, stderr = await process.communicate(input=b"y\n")

            success = process.returncode == 0

            print(stdout.decode("utf-8"))
            if stderr:
                print("エラー出力:")
                print(stderr.decode("utf-8"))

            # 結果ファイルを読み込み
            result_file = self.backend_dir / "test_results.json"
            if result_file.exists():
                with open(result_file, encoding="utf-8") as f:
                    self.results["test_execution"] = json.load(f)

            status = "成功" if success else "失敗"
            print(f"\n総合テスト: {status}")

            return success

        except Exception as e:
            print(f"❌ 総合テスト実行エラー: {e}")
            self.results["test_execution"] = {"error": str(e)}
            return False

    def run_log_analysis(self) -> bool:
        """ログ分析の実行"""
        print("\n" + "=" * 60)
        print("ステップ7-2: ログ分析")
        print("=" * 60)

        try:
            # log_monitor.pyを実行
            result = subprocess.run(
                [sys.executable, "log_monitor.py", "--output", "log_analysis.json"],
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            print(result.stdout)
            if result.stderr:
                print("エラー出力:")
                print(result.stderr)

            # 結果ファイルを読み込み
            result_file = self.backend_dir / "log_analysis.json"
            if result_file.exists():
                with open(result_file, encoding="utf-8") as f:
                    self.results["log_analysis"] = json.load(f)

            success = result.returncode == 0
            status = "成功" if success else "失敗"
            print(f"\nログ分析: {status}")

            return success

        except Exception as e:
            print(f"❌ ログ分析実行エラー: {e}")
            self.results["log_analysis"] = {"error": str(e)}
            return False

    def run_database_inspection(self) -> bool:
        """データベース検査の実行"""
        print("\n" + "=" * 60)
        print("ステップ7-3: データベース検査")
        print("=" * 60)

        try:
            # db_inspector.pyを実行
            result = subprocess.run(
                [sys.executable, "db_inspector.py", "--output", "db_inspection.json"],
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                timeout=30,
            )

            print(result.stdout)
            if result.stderr:
                print("エラー出力:")
                print(result.stderr)

            # 結果ファイルを読み込み
            result_file = self.backend_dir / "db_inspection.json"
            if result_file.exists():
                with open(result_file, encoding="utf-8") as f:
                    self.results["database_inspection"] = json.load(f)

            success = result.returncode == 0
            status = "成功" if success else "失敗"
            print(f"\nデータベース検査: {status}")

            return success

        except Exception as e:
            print(f"❌ データベース検査実行エラー: {e}")
            self.results["database_inspection"] = {"error": str(e)}
            return False

    def generate_final_report(self) -> dict:
        """最終レポートの生成"""
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        # 各テストの成功状況を判定
        test_success = self.results["test_execution"].get("overall_success", False)
        log_success = "error" not in self.results["log_analysis"]
        db_success = "error" not in self.results["database_inspection"]

        overall_success = test_success and log_success and db_success

        report = {
            "step7_completion": {
                "overall_success": overall_success,
                "execution_time": duration,
                "start_time": self.start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
            "test_results": {
                "comprehensive_tests": {"success": test_success, "details": self.results["test_execution"]},
                "log_analysis": {"success": log_success, "details": self.results["log_analysis"]},
                "database_inspection": {"success": db_success, "details": self.results["database_inspection"]},
            },
            "summary": {
                "total_tests": 3,
                "passed_tests": sum([test_success, log_success, db_success]),
                "failed_tests": 3 - sum([test_success, log_success, db_success]),
            },
        }

        return report

    def print_final_report(self, report: dict):
        """最終レポートの出力"""
        print("\n" + "=" * 60)
        print("ステップ7: 最終レポート")
        print("=" * 60)

        summary = report["summary"]
        step7 = report["step7_completion"]

        print(f"実行時間: {step7['execution_time']:.2f}秒")
        print(f"開始時刻: {step7['start_time']}")
        print(f"終了時刻: {step7['end_time']}")

        print("\n--- テスト結果サマリー ---")
        print(f"総テスト数: {summary['total_tests']}")
        print(f"成功: {summary['passed_tests']}")
        print(f"失敗: {summary['failed_tests']}")

        print("\n--- 詳細結果 ---")
        for test_name, result in report["test_results"].items():
            status = "✅ 成功" if result["success"] else "❌ 失敗"
            print(f"{test_name}: {status}")

        if step7["overall_success"]:
            print("\n🎉 ステップ7: 最終確認とテスト - 完了")
            print("全ての機能が正常に動作しています！")
        else:
            print("\n❌ ステップ7: 一部のテストが失敗しました")
            print("詳細は上記の結果を確認してください。")

        print("\n📋 詳細レポートは step7_final_report.json に保存されます")

    async def run_all_tests(self) -> bool:
        """全テストの実行"""
        print("AI Community Backend - ステップ7: 最終確認とテスト")
        print("=" * 60)

        # 事前チェック
        if not self.check_dependencies():
            return False

        if not self.check_server_status():
            print("\n⚠️ サーバーが起動していませんが、一部のテストは実行可能です")
            response = input("続行しますか？ (y/N): ").strip().lower()
            if response != "y":
                return False

        # 各テストの実行
        test_results = []

        # 総合テスト
        test_results.append(await self.run_comprehensive_tests())

        # ログ分析
        test_results.append(self.run_log_analysis())

        # データベース検査
        test_results.append(self.run_database_inspection())

        # 最終レポート生成
        report = self.generate_final_report()
        self.print_final_report(report)

        # レポートをファイルに保存
        report_file = self.backend_dir / "step7_final_report.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)

        return report["step7_completion"]["overall_success"]


def main():
    """メイン実行関数"""
    runner = Step7TestRunner()

    try:
        success = asyncio.run(runner.run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nテストが中断されました。")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n予期しないエラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
