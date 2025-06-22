"""自動会話タイマー管理モジュール."""

import asyncio
import logging
from contextlib import asynccontextmanager

try:
    # パッケージとして実行される場合
    from ..database import SessionLocal
    from .auto_conversation import handle_auto_conversation_check
    from .conversation_config import get_conversation_config
except ImportError:
    # 直接実行される場合
    from ai.auto_conversation import handle_auto_conversation_check
    from ai.conversation_config import get_conversation_config
    from database import SessionLocal

logger = logging.getLogger(__name__)


class ConversationTimer:
    """自動会話のタイマー管理クラス."""

    def __init__(self):
        """初期化."""
        self._task: asyncio.Task | None = None
        self._running = False
        self.config = get_conversation_config()

    def is_running(self) -> bool:
        """タイマーが動作中かどうかを確認."""
        return self._running and self._task is not None and not self._task.done()

    async def start(self) -> None:
        """タイマーを開始."""
        if self.is_running():
            logger.warning("自動会話タイマーは既に動作中です")
            return

        if not self.config.enabled:
            logger.info("自動会話機能が無効のため、タイマーを開始しません")
            return

        logger.info("自動会話タイマーを開始")
        self._running = True
        self._task = asyncio.create_task(self._timer_loop())

    async def stop(self) -> None:
        """タイマーを停止."""
        if not self.is_running():
            logger.debug("自動会話タイマーは動作していません")
            return

        logger.info("自動会話タイマーを停止中...")
        self._running = False

        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                logger.info("自動会話タイマーが正常に停止されました")
            except Exception as e:
                logger.error(f"自動会話タイマー停止時にエラー: {str(e)}")
            finally:
                self._task = None

    async def _timer_loop(self) -> None:
        """タイマーのメインループ."""
        # チェック間隔（15秒間隔でチェックして正確な間隔を実現）
        check_interval = 15

        logger.info(
            f"自動会話タイマーループ開始: check_interval={check_interval}秒, conversation_interval={self.config.conversation_interval}秒, target_channel={self.config.target_channel_id}"
        )

        try:
            while self._running:
                try:
                    await self._check_and_execute_auto_conversation()
                except Exception as e:
                    logger.error(f"自動会話チェック中にエラー: {str(e)}")

                # 15秒間隔でチェック
                await asyncio.sleep(check_interval)

        except asyncio.CancelledError:
            logger.info("自動会話タイマーループがキャンセルされました")
            raise
        except Exception as e:
            logger.error(f"自動会話タイマーループで予期しないエラー: {str(e)}")

    async def _check_and_execute_auto_conversation(self) -> None:
        """自動会話のチェック・実行."""
        db = SessionLocal()
        try:
            # 対象チャンネルで自動会話をチェック
            executed = await handle_auto_conversation_check(self.config.target_channel_id, db)

            if executed:
                logger.info("自動会話が実行されました")
            else:
                logger.debug("自動会話の実行条件が満たされていません")

        except Exception as e:
            logger.error(f"自動会話チェック・実行でエラー: {str(e)}")
        finally:
            db.close()


# グローバルタイマーインスタンス
_conversation_timer: ConversationTimer | None = None


def get_conversation_timer() -> ConversationTimer:
    """ConversationTimerのシングルトンインスタンスを取得."""
    global _conversation_timer
    if _conversation_timer is None:
        _conversation_timer = ConversationTimer()
    return _conversation_timer


@asynccontextmanager
async def conversation_timer_lifespan():
    """自動会話タイマーのライフサイクル管理."""
    timer = get_conversation_timer()
    try:
        await timer.start()
        yield timer
    finally:
        await timer.stop()


# 便利関数
async def start_conversation_timer() -> None:
    """自動会話タイマーを開始."""
    timer = get_conversation_timer()
    await timer.start()


async def stop_conversation_timer() -> None:
    """自動会話タイマーを停止."""
    timer = get_conversation_timer()
    await timer.stop()


def is_conversation_timer_running() -> bool:
    """自動会話タイマーが動作中かどうかを確認."""
    timer = get_conversation_timer()
    return timer.is_running()
