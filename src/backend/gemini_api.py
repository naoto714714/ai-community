"""Gemini API統合モジュール."""

import asyncio
import os
from pathlib import Path

import google.generativeai as genai  # type: ignore
from google.generativeai.types import GenerateContentResponse  # type: ignore


class GeminiAPIClient:
    """Gemini APIクライアント."""

    def __init__(self) -> None:
        """初期化."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        genai.configure(api_key=self.api_key)  # type: ignore
        self.model = genai.GenerativeModel("gemini-pro")  # type: ignore
        self._system_prompt: str | None = None
        self._load_system_prompt()

    def _load_system_prompt(self) -> None:
        """システムプロンプトを読み込む."""
        prompt_path = Path(__file__).parent.parent.parent / "prompts" / "001_ハルト.md"
        try:
            with open(prompt_path, encoding="utf-8") as f:
                self._system_prompt = f.read()
        except FileNotFoundError:
            self._system_prompt = """
あなたは「ハルト」という名前の明るく親しみやすい男性です。
太陽のように温かく、人とのコミュニケーションを大切にする性格です。
親しみやすく、フレンドリーな口調で話してください。
"""

    async def generate_response(self, user_message: str, max_retries: int = 5) -> str:
        """
        ユーザーメッセージに対する応答を生成する.

        Args:
            user_message: ユーザーからのメッセージ
            max_retries: 最大リトライ回数

        Returns:
            AIの応答テキスト
        """
        prompt = f"{self._system_prompt}\n\nユーザー: {user_message}\nハルト:"

        for attempt in range(max_retries):
            try:
                # 非同期でGemini APIを呼び出し
                loop = asyncio.get_event_loop()
                response: GenerateContentResponse = await loop.run_in_executor(None, self._sync_generate, prompt)

                if response.text:
                    return response.text.strip()
                else:
                    raise Exception("Empty response from Gemini API")

            except Exception:
                if attempt == max_retries - 1:
                    # 最後のリトライでも失敗した場合
                    return "通信に失敗しました😅 もう一度試してみてください！"

                # 指数バックオフでリトライ
                wait_time = 2**attempt
                await asyncio.sleep(wait_time)
                continue

        return "通信に失敗しました😅 もう一度試してみてください！"

    def _sync_generate(self, prompt: str) -> GenerateContentResponse:
        """同期的にコンテンツを生成する（run_in_executor用）."""
        return self.model.generate_content(prompt)  # type: ignore

    def should_respond_to_message(self, message: str) -> bool:
        """
        メッセージに応答すべきかどうかを判定する.

        Args:
            message: チェックするメッセージ

        Returns:
            応答すべき場合True
        """
        return "@ai" in message.lower()


# グローバルインスタンス
gemini_client: GeminiAPIClient | None = None


def get_gemini_client() -> GeminiAPIClient:
    """Gemini APIクライアントのシングルトンインスタンスを取得."""
    global gemini_client
    if gemini_client is None:
        gemini_client = GeminiAPIClient()
    return gemini_client
