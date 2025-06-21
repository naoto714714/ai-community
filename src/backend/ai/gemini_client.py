"""Gemini API統合モジュール."""

import asyncio
import logging
import os
from pathlib import Path

import google.generativeai as genai  # type: ignore
from google.generativeai.types import GenerateContentResponse  # type: ignore

logger = logging.getLogger(__name__)


class GeminiAPIClient:
    """Gemini APIクライアント."""

    # フォールバックメッセージの一元管理
    FALLBACK_MESSAGE = "通信に失敗しました😅 もう一度試してみてください！"

    def __init__(self) -> None:
        """初期化."""
        logger.info("GeminiAPIClient初期化開始")
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY環境変数が設定されていません")
            raise ValueError("GEMINI_API_KEY environment variable is required")

        logger.info("GEMINI_API_KEY確認済み")
        genai.configure(api_key=self.api_key)  # type: ignore
        self.model = genai.GenerativeModel("gemini-1.5-flash")  # type: ignore
        logger.info("Gemini 1.5 Flashモデル初期化完了")
        self._system_prompt: str | None = None
        self._load_system_prompt()

    def _load_system_prompt(self) -> None:
        """システムプロンプトを読み込む."""
        # 環境変数から基本パスを取得、デフォルトはプロジェクトルート
        base_path = os.getenv("AI_COMMUNITY_BASE_PATH")
        if base_path:
            prompt_path = Path(base_path) / "prompts" / "001_ハルト.md"
        else:
            # フォールバック: プロジェクトルートを推測
            prompt_path = Path(__file__).parent.parent.parent.parent / "prompts" / "001_ハルト.md"

        logger.info(f"プロンプトファイル読み込み試行: {prompt_path}")
        try:
            with open(prompt_path, encoding="utf-8") as f:
                self._system_prompt = f.read()
            logger.info(f"プロンプトファイル読み込み成功: 文字数={len(self._system_prompt)}")
        except FileNotFoundError:
            logger.warning(f"プロンプトファイルが見つかりません: {prompt_path}、デフォルトプロンプトを使用")
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
        logger.info(f"Gemini API応答生成開始: user_message='{user_message[:50]}...' max_retries={max_retries}")
        prompt = f"{self._system_prompt}\n\nユーザー: {user_message}\nハルト:"

        for attempt in range(max_retries):
            try:
                logger.info(f"Gemini API呼び出し試行 {attempt + 1}/{max_retries}")
                # 非同期でGemini APIを呼び出し
                loop = asyncio.get_event_loop()
                response: GenerateContentResponse = await loop.run_in_executor(None, self._sync_generate, prompt)

                if response.text:
                    response_text = response.text.strip()
                    logger.info(f"Gemini API応答成功: response_length={len(response_text)}")
                    return response_text

                logger.warning("Gemini APIから空の応答を受信")
                raise Exception("Empty response from Gemini API")

            except Exception as e:
                # より具体的な例外処理
                if "generation" in str(e).lower() or "content" in str(e).lower():
                    logger.error(f"Gemini API生成エラー (試行 {attempt + 1}/{max_retries}): {str(e)}")
                else:
                    logger.error(f"Gemini API呼び出し失敗 (試行 {attempt + 1}/{max_retries}): {str(e)}")

                if attempt == max_retries - 1:
                    # 最後のリトライでも失敗した場合
                    logger.error("Gemini API: 全リトライ試行が失敗、フォールバック応答を返す")
                    return self.FALLBACK_MESSAGE

                # 指数バックオフでリトライ
                wait_time = 2**attempt
                logger.info(f"Gemini API: {wait_time}秒後にリトライします")
                await asyncio.sleep(wait_time)
                continue

        return self.FALLBACK_MESSAGE

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
        result = "@ai" in message.lower()
        logger.debug(f"@AI検出: '{message[:50]}...' -> {result}")
        return result


# グローバルインスタンス
gemini_client: GeminiAPIClient | None = None


def get_gemini_client() -> GeminiAPIClient:
    """Gemini APIクライアントのシングルトンインスタンスを取得."""
    global gemini_client
    if gemini_client is None:
        logger.info("新しいGeminiAPIClientインスタンスを作成")
        gemini_client = GeminiAPIClient()
    return gemini_client
