"""Gemini API統合モジュール."""

import asyncio
import logging
import os
import re
import threading
from pathlib import Path

import google.generativeai as genai  # type: ignore
from google.generativeai.types import GenerateContentResponse  # type: ignore
from sqlalchemy.orm import Session

# 動的インポートを避けるための静的インポート
try:
    from .. import crud
except ImportError:
    import crud

logger = logging.getLogger(__name__)


class GeminiAPIClient:
    """Gemini APIクライアント."""

    # フォールバックメッセージの一元管理
    FALLBACK_MESSAGE = "通信に失敗しました😅 もう一度試してみてください！"

    # AI ID定数
    AI_HARUTO_ID = "ai_haruto"

    def __init__(self) -> None:
        """初期化."""
        logger.info("GeminiAPIClient初期化開始")
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY環境変数が設定されていません")
            raise ValueError("GEMINI_API_KEY environment variable is required")

        logger.info("GEMINI_API_KEY確認済み")
        genai.configure(api_key=self.api_key)  # type: ignore
        self.model = genai.GenerativeModel("gemini-2.5-flash-preview-05-20")  # type: ignore
        logger.info("Gemini 2.5 Flash Preview 05-20モデル初期化完了")
        self._system_prompt: str | None = None
        self._load_system_prompt()

    def _load_system_prompt(self) -> None:
        """システムプロンプトを読み込む."""
        # 環境変数から基本パスを取得
        base_path = os.getenv("AI_COMMUNITY_BASE_PATH")
        if not base_path:
            # より安全なフォールバック：現在のディレクトリから検索
            current = Path(__file__).parent
            while current != current.parent:
                prompt_dir = current / "prompts"
                if prompt_dir.exists():
                    base_path = str(current)
                    break
                current = current.parent

            if not base_path:
                logger.error("プロジェクトルートが見つかりません")
                raise FileNotFoundError("プロジェクトルートの特定に失敗しました")

        prompt_path = Path(base_path) / "prompts" / "001_ハルト.md"

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

    def _format_conversation_history(self, messages: list) -> str:
        """過去の会話履歴をフォーマットする"""
        if not messages:
            return ""

        history_lines = ["===== 過去の会話履歴 ====="]
        for msg in messages:
            # user_typeを使ってAIかユーザーかを判定
            if hasattr(msg, "user_type") and msg.user_type == "ai":
                # AIの場合は、どのAIかを明確にする
                if msg.user_id == self.AI_HARUTO_ID:
                    history_lines.append(f"[AI:ハルト]: {msg.content}")
                else:
                    # 他のAIの場合（将来対応）
                    history_lines.append(f"[AI:{msg.user_name}]: {msg.content}")
            else:
                # ユーザーの場合
                history_lines.append(f"[ユーザー:{msg.user_name}]: {msg.content}")

        history_lines.append("")  # 空行を追加
        return "\n".join(history_lines)

    async def _fetch_conversation_history(self, channel_id: str, db_session: Session) -> str:
        """会話履歴を取得してフォーマットする"""
        try:
            recent_messages = crud.get_recent_channel_messages(db_session, channel_id, limit=30)
            logger.debug(f"デバッグ: 取得したメッセージ数={len(recent_messages)}")
            for i, msg in enumerate(recent_messages[-5:]):  # 最新5件をログ出力
                logger.debug(f"デバッグ: メッセージ{i}: user_id={msg.user_id}, content='{msg.content[:30]}...'")
            conversation_history = self._format_conversation_history(recent_messages)
            logger.info(f"過去の会話履歴を取得: {len(recent_messages)}件のメッセージ")
            logger.debug(f"デバッグ: conversation_history の長さ={len(conversation_history)}")
            return conversation_history
        except Exception as e:
            logger.error(f"過去の会話履歴取得エラー: {str(e)}")
            import traceback

            logger.error(f"エラー詳細: {traceback.format_exc()}")
            return ""

    def _build_prompt(self, user_message: str, conversation_history: str) -> str:
        """プロンプトを構築する"""
        if conversation_history:
            return f"{self._system_prompt}\n\n{conversation_history}===== 現在の質問 =====\n[ユーザー]: {user_message}\n[AI:ハルト]:"
        return f"{self._system_prompt}\n\n[ユーザー]: {user_message}\n[AI:ハルト]:"

    async def generate_response(
        self, user_message: str, channel_id: str | None = None, db_session: Session | None = None, max_retries: int = 5
    ) -> str:
        """
        ユーザーメッセージに対する応答を生成する.

        Args:
            user_message: ユーザーからのメッセージ
            channel_id: チャンネルID（過去の会話履歴取得用）
            db_session: データベースセッション
            max_retries: 最大リトライ回数

        Returns:
            AIの応答テキスト
        """
        logger.info(f"Gemini API応答生成開始: user_message='{user_message[:50]}...' max_retries={max_retries}")

        # 過去の会話履歴を取得
        conversation_history = ""
        logger.debug(f"デバッグ: channel_id={channel_id}, db_session={db_session is not None}")
        if channel_id and db_session:
            conversation_history = await self._fetch_conversation_history(channel_id, db_session)
        else:
            logger.debug(
                f"デバッグ: 会話履歴取得をスキップ - channel_id={channel_id}, db_session={db_session is not None}"
            )

        # プロンプトを構築
        prompt = self._build_prompt(user_message, conversation_history)
        if conversation_history:
            logger.debug("デバッグ: 会話履歴付きプロンプトを使用")
        else:
            logger.debug("デバッグ: 会話履歴なしプロンプトを使用")

        # プロンプトの一部をログに出力（デバッグ用、本番では出力されない）
        logger.debug(f"デバッグ: プロンプト長={len(prompt)}")
        if len(prompt) > 2000:
            logger.debug(f"デバッグ: プロンプト先頭1000文字: {prompt[:1000]}...")
        else:
            logger.debug(f"デバッグ: プロンプト全体: {prompt}")

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
                error_type = type(e).__name__
                logger.error(f"Gemini API呼び出し失敗 (試行 {attempt + 1}/{max_retries}): {error_type}: {str(e)}")

                # 特定のエラータイプに対する処理が必要な場合
                # if isinstance(e, SpecificAPIError):
                #     # 特別な処理

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
        """
        同期的にコンテンツを生成する（run_in_executor用）.

        Gemini 2.5 Flash Preview 05-20用の基本設定でコンテンツを生成します。
        """
        # Gemini 2.5 Flash用の基本設定
        generation_config = {
            "temperature": 0.7,
            "max_output_tokens": 1000,
        }

        return self.model.generate_content(prompt, generation_config=generation_config)  # type: ignore

    def should_respond_to_message(self, message: str) -> bool:
        """
        メッセージに応答すべきかどうかを判定する.

        Args:
            message: チェックするメッセージ

        Returns:
            応答すべき場合True
        """
        # 日本語環境に対応した@AI検出（全角スペースも考慮）
        # (?:^|[\s　]) - 文頭または半角・全角空白文字の後
        # @ai - @aiのリテラル（大文字小文字区別なし）
        # (?=[\s　]|$) - 半角・全角空白文字または文末の前
        pattern = r"(?:^|[\s　])@ai(?=[\s　]|$)"
        result = bool(re.search(pattern, message.lower()))
        logger.debug(f"@AI検出: '{message[:50]}...' -> {result}")
        return result


# グローバルインスタンス
gemini_client: GeminiAPIClient | None = None
_lock = threading.Lock()


def get_gemini_client() -> GeminiAPIClient:
    """Gemini APIクライアントのシングルトンインスタンスを取得."""
    global gemini_client
    if gemini_client is None:
        with _lock:
            # ダブルチェックロッキング
            if gemini_client is None:
                logger.info("新しいGeminiAPIClientインスタンスを作成")
                gemini_client = GeminiAPIClient()
    return gemini_client
