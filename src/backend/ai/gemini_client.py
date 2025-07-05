"""Gemini API統合モジュール."""

import asyncio
import logging
import os
import re
import sys
import threading
from pathlib import Path

# 動的インポートを避けるための静的インポート
try:
    # パッケージとして実行される場合
    from .. import crud
    from ..constants.ai_config import DEFAULT_CONVERSATION_HISTORY_LIMIT, DEFAULT_MAX_OUTPUT_TOKENS
    from .personality_manager import AIPersonality, get_personality_manager
except ImportError:
    # 直接実行される場合
    import crud
    from ai.personality_manager import AIPersonality, get_personality_manager
    from constants.ai_config import DEFAULT_CONVERSATION_HISTORY_LIMIT, DEFAULT_MAX_OUTPUT_TOKENS
from google import genai  # type: ignore
from google.genai import types  # type: ignore
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class GeminiAPIClient:
    """Gemini APIクライアント."""

    # フォールバックメッセージの一元管理
    FALLBACK_MESSAGE = "通信に失敗しました😅 もう一度試してみてください！"

    # フォールバック人格（システムメッセージ用）
    FALLBACK_AI_NAME = "システム"
    FALLBACK_AI_ID = "ai_system"

    def __init__(self) -> None:
        """初期化."""
        logger.info("GeminiAPIClient初期化開始")
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY環境変数が設定されていません")
            raise ValueError("GEMINI_API_KEY environment variable is required")

        logger.info("GEMINI_API_KEY確認済み")
        self.client = genai.Client(api_key=self.api_key)  # type: ignore
        logger.info("Gemini 2.5 Flash Preview 05-20クライアント初期化完了")
        self.personality_manager = get_personality_manager()

        # システム人格を作成
        self.system_personality = AIPersonality(
            file_name="system",
            name=self.FALLBACK_AI_NAME,
            prompt_content="システムメッセージ",
            user_id=self.FALLBACK_AI_ID,
        )
        self._fallback_prompt: str | None = None
        self._load_fallback_prompt()

    def _load_fallback_prompt(self) -> None:
        """フォールバック用システムプロンプトを読み込む."""
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

        # フォールバック用のシンプルなプロンプトを設定
        self._fallback_prompt = """
あなたは親しみやすいAIアシスタントです。
ユーザーとの会話を楽しみ、役に立つ情報を提供します。
"""
        logger.info("フォールバックプロンプトを設定")

    def _select_random_personality(self, exclude_user_id: str | None = None) -> AIPersonality:
        """ランダムに人格を選択し、フォールバックを管理.

        Args:
            exclude_user_id: 除外するAI人格のuser_id（連続発言防止用）

        Returns:
            選択された人格

        """
        try:
            # ランダムに人格を選択（除外対象考慮）
            personality = self.personality_manager.get_random_personality(exclude_user_id)
            if personality:
                if exclude_user_id:
                    logger.info(
                        f"連続発言防止考慮でランダム人格選択: {personality.name} (user_id: {personality.user_id}), 除外対象: {exclude_user_id}"
                    )
                else:
                    logger.debug(f"ランダム人格選択: {personality.name} (user_id: {personality.user_id})")
                return personality
        except Exception as e:
            logger.error(f"人格選択エラー: {e!s}")

        # フォールバック人格を返す
        logger.warning("フォールバック人格を使用")
        return AIPersonality(
            file_name="fallback.md",
            name=self.FALLBACK_AI_NAME,
            prompt_content=self._fallback_prompt or "親しみやすいAIです。",
            user_id=self.FALLBACK_AI_ID,
        )

    def _format_conversation_history(self, messages: list) -> str:
        """過去の会話履歴をフォーマットする"""
        if not messages:
            return ""

        history_lines = ["===== 過去の会話履歴 ====="]
        for msg in messages:
            # AIとユーザーの区別なく、名前のみで表示
            history_lines.append(f"{msg.user_name}: {msg.content}")

        history_lines.append("")  # 空行を追加
        return "\n".join(history_lines)

    async def _fetch_conversation_history(self, channel_id: str, db_session: Session) -> str:
        """会話履歴を取得してフォーマットする"""
        try:
            recent_messages = crud.get_recent_channel_messages(
                db_session, channel_id, limit=DEFAULT_CONVERSATION_HISTORY_LIMIT
            )
            logger.debug(f"デバッグ: 取得したメッセージ数={len(recent_messages)}")
            for i, msg in enumerate(recent_messages[-5:]):  # 最新5件をログ出力
                logger.debug(f"デバッグ: メッセージ{i}: user_id={msg.user_id}, content='{msg.content[:30]}...'")
            conversation_history = self._format_conversation_history(recent_messages)
            logger.info(f"過去の会話履歴を取得: {len(recent_messages)}件のメッセージ")
            logger.debug(f"デバッグ: conversation_history の長さ={len(conversation_history)}")
            return conversation_history
        except Exception as e:
            logger.error(f"過去の会話履歴取得エラー: {e!s}")
            import traceback

            logger.error(f"エラー詳細: {traceback.format_exc()}")
            return ""

    async def generate_response(
        self,
        user_message: str,
        channel_id: str | None = None,
        db_session: Session | None = None,
        max_retries: int = 5,
        exclude_user_id: str | None = None,
    ) -> tuple[str, AIPersonality]:
        """ユーザーメッセージに対する応答を生成する.

        Args:
            user_message: ユーザーからのメッセージ
            channel_id: チャンネルID（過去の会話履歴取得用）
            db_session: データベースセッション
            max_retries: 最大リトライ回数
            exclude_user_id: 除外するAI人格のuser_id（連続発言防止用）

        Returns:
            tuple[AIの応答テキスト, 選択された人格]

        """
        logger.info(f"Gemini API応答生成開始: user_message='{user_message[:50]}...' max_retries={max_retries}")

        # ランダムに人格を選択（連続発言防止考慮）
        personality = self._select_random_personality(exclude_user_id)
        logger.info(f"選択された人格: {personality.name}")

        # 過去の会話履歴を取得
        conversation_history = ""
        logger.debug(f"デバッグ: channel_id={channel_id}, db_session={db_session is not None}")
        if channel_id and db_session:
            conversation_history = await self._fetch_conversation_history(channel_id, db_session)
        else:
            logger.debug(
                f"デバッグ: 会話履歴取得をスキップ - channel_id={channel_id}, db_session={db_session is not None}"
            )

        # 新しいAPIではsystem_instructionでプロンプト設定
        logger.debug(f"選択された人格のプロンプト長: {len(personality.prompt_content)}")
        if conversation_history:
            logger.debug(f"会話履歴長: {len(conversation_history)}")
            # 会話履歴がある場合は文脈も含めてメッセージを構築
            enhanced_message = f"{conversation_history}\n\n現在の質問: {user_message}"
        else:
            enhanced_message = user_message

        for attempt in range(max_retries):
            try:
                logger.info(f"Gemini API呼び出し試行 {attempt + 1}/{max_retries}")
                # 非同期でGemini APIを呼び出し
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, self._sync_generate, enhanced_message, personality)

                if hasattr(response, "text") and response.text:  # type: ignore
                    response_text = response.text.strip()  # type: ignore
                    if response_text:  # 空でない文字列かチェック
                        logger.info(
                            f"Gemini API応答成功: response_length={len(response_text)}, personality={personality.name}"
                        )
                        return response_text, personality

                logger.warning("Gemini APIから空の応答を受信")
                raise Exception("Empty response from Gemini API")

            except Exception as e:
                # より具体的な例外処理
                error_type = type(e).__name__
                error_message = str(e)

                # 429エラー（Rate Limit Exceeded）の特別処理
                if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
                    logger.error(
                        "🚨 Gemini API Rate Limit超過エラー: 日次クォータ（250リクエスト/日）を超過しました。24時間待機してから再度お試しください。システムを停止します..."
                    )

                    # システムを停止
                    sys.exit(1)

                logger.error(
                    f"Gemini API呼び出し失敗 (試行 {attempt + 1}/{max_retries}): {error_type}: {error_message}"
                )

                if attempt == max_retries - 1:
                    # 最後のリトライでも失敗した場合
                    logger.error("Gemini API: 全リトライ試行が失敗、フォールバック応答を返す")
                    return self.FALLBACK_MESSAGE, self.system_personality

                # 指数バックオフでリトライ
                wait_time = 2**attempt
                logger.info(f"Gemini API: {wait_time}秒後にリトライします")
                await asyncio.sleep(wait_time)
                continue

        return self.FALLBACK_MESSAGE, self.system_personality

    def _sync_generate(self, user_message: str, personality: AIPersonality) -> object:
        """同期的にコンテンツを生成する（run_in_executor用）.

        新しいGoogle Genai APIを使用してコンテンツを生成します。

        Args:
            user_message: ユーザーメッセージ
            personality: AI人格

        Returns:
            Gemini APIのレスポンスオブジェクト

        Raises:
            Exception: API呼び出しに失敗した場合（認証エラー、ネットワークエラーなど）

        """
        # 環境変数からmax_output_tokensをカスタマイズ可能にする（安全な変換処理）
        try:
            max_tokens = int(os.getenv("AI_MAX_OUTPUT_TOKENS", DEFAULT_MAX_OUTPUT_TOKENS))
        except (ValueError, TypeError):
            logger.warning(
                f"Invalid AI_MAX_OUTPUT_TOKENS value: {os.getenv('AI_MAX_OUTPUT_TOKENS')}. "
                f"Using default: {DEFAULT_MAX_OUTPUT_TOKENS}"
            )
            max_tokens = DEFAULT_MAX_OUTPUT_TOKENS

        response = self.client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=user_message,
            config=types.GenerateContentConfig(  # type: ignore
                system_instruction=personality.prompt_content,
                temperature=0.9,
                max_output_tokens=max_tokens,
            ),
        )
        return response

    def should_respond_to_message(self, message: str) -> bool:
        """メッセージに応答すべきかどうかを判定する.

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
