import json
import logging
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any, TypedDict

from fastapi import WebSocket
from sqlalchemy.orm import Session

try:
    from . import crud
    from .gemini_api import get_gemini_client
    from .schemas import MessageCreate
except ImportError:
    import crud
    from gemini_api import get_gemini_client
    from schemas import MessageCreate


class WebSocketMessageData(TypedDict):
    """WebSocketメッセージのdata部分の型定義"""

    id: str
    channel_id: str
    user_id: str
    user_name: str
    content: str
    timestamp: str
    is_own_message: bool


class WebSocketMessage(TypedDict):
    """WebSocketメッセージの型定義"""

    type: str
    data: WebSocketMessageData | None


logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        """初期化"""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """新しいWebSocket接続を追加"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"新しいWebSocket接続が登録されました。総数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """指定WebSocket接続を削除"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket接続が切断されました。総数: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """特定のクライアントにメッセージを送信"""
        try:
            await websocket.send_text(message)
        except Exception:
            # 接続が切断されている場合は削除
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        """
        全ての接続中のクライアントにメッセージをブロードキャスト

        接続状態の管理:
        1. 接続リストのコピーを作成して、イテレート中の変更を防ぐ
        2. 各接続の状態を事前にチェックし、切断済みの接続をマーク
        3. メッセージ送信に失敗した接続もマーク
        4. 最後に切断された接続をリストから削除

        この方式により、ネットワーク障害や予期しない切断に対して
        堅牢な接続管理を実現している
        """
        connections_to_remove = []
        for connection in self.active_connections.copy():  # リストのコピーを作成して安全にイテレート
            try:
                # WebSocket接続状態を厳密にチェック
                # client_stateがDISCONNECTEDの場合は既に切断済み
                if connection.client_state.name == "DISCONNECTED":
                    connections_to_remove.append(connection)
                    continue
                # メッセージ送信を試行
                await connection.send_text(message)
            except Exception:
                # 送信に失敗した場合は接続が切断されているとみなす
                connections_to_remove.append(connection)

        # 切断された接続をアクティブリストから削除
        for conn in connections_to_remove:
            self.disconnect(conn)


manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """ConnectionManagerのインスタンスを取得（テスト用）"""
    return manager


def save_message_with_session_management(
    message_create_func: Callable[[Session], Any],
    db_session: Session | None = None,
) -> Any:
    """
    セッション管理を共通化したメッセージ保存ヘルパー関数

    Args:
        message_create_func: セッションを受け取ってメッセージを作成する関数
        db_session: オプショナルセッション。テスト環境で使用される。
                    Noneの場合は新しいセッションを作成（本番環境）

    Returns:
        保存されたメッセージオブジェクト
    """
    try:
        from .database import SessionLocal
    except ImportError:
        from database import SessionLocal

    if db_session is not None:
        # テスト環境: 提供されたセッションを使用（commit/closeは呼び出し元で管理）
        try:
            return message_create_func(db_session)
        except Exception:
            db_session.rollback()
            raise
    else:
        # 本番環境: 新しいセッションを作成してcommit/rollback/closeを管理
        db = SessionLocal()
        try:
            return message_create_func(db)
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()


async def handle_websocket_message(
    websocket: WebSocket,
    data: dict[str, Any],
    db_session: Session | None = None,
):
    """WebSocketメッセージの処理"""
    # 型安全性のためにWebSocketMessage型を想定しているが、
    # 実行時は辞書として扱う（TypedDictは実行時は通常の辞書）
    message_type = data.get("type")
    message_data = data.get("data")

    if message_type == "message:send":
        try:
            # 共通のセッション管理ヘルパーを使用
            message_create = MessageCreate.model_validate(message_data)
            saved_message = save_message_with_session_management(
                lambda session: crud.create_message(session, message_create), db_session
            )

            # 保存成功をクライアントに通知
            response = {"type": "message:saved", "data": {"id": saved_message.id, "success": True}}
            await manager.send_personal_message(json.dumps(response), websocket)

            logger.info(f"メッセージが保存されました: {saved_message.id}")

            # ユーザーメッセージを全クライアントにブロードキャスト
            user_broadcast_message = {
                "type": "message:broadcast",
                "data": {
                    "id": saved_message.id,
                    "channel_id": saved_message.channel_id,
                    "user_id": saved_message.user_id,
                    "user_name": saved_message.user_name,
                    "content": saved_message.content,
                    "timestamp": saved_message.timestamp.isoformat(),
                    "is_own_message": False,  # ブロードキャスト時は全て他人のメッセージとして表示
                },
            }
            await manager.broadcast(json.dumps(user_broadcast_message))
            logger.info(f"ユーザーメッセージをブロードキャスト: {saved_message.id}")

            # AI応答の処理
            await handle_ai_response(message_data, db_session)

        except Exception as e:
            logger.error(f"メッセージ保存エラー: {str(e)}")
            # デバッグのため詳細なエラー情報もログに出力
            import traceback

            logger.error(f"詳細なエラー情報: {traceback.format_exc()}")

            # エラーをクライアントに通知（情報漏洩対策済み）
            # メッセージIDを安全に取得（None値の場合も考慮）
            message_id = None
            if message_data and isinstance(message_data, dict):
                message_id = message_data.get("id")

            error_response = {
                "type": "message:error",
                "data": {
                    "id": message_id,
                    "success": False,
                    "error": "メッセージの保存に失敗しました",  # 詳細なエラー情報を隠蔽
                },
            }
            await manager.send_personal_message(json.dumps(error_response), websocket)

    else:
        logger.warning(f"未知のメッセージタイプ: {message_type}")


async def handle_ai_response(message_data: dict[str, Any] | None, db_session: Session | None = None):
    """AI応答の処理"""
    import time

    start_time = time.time()

    if not message_data or not isinstance(message_data, dict):
        return

    user_message = message_data.get("content", "")
    channel_id = message_data.get("channel_id", "")
    logger.info(f"AI応答処理開始: channel_id={channel_id}, message='{user_message[:50]}...'")

    # @AI が含まれているかチェック（大文字小文字区別なし）
    gemini_client = get_gemini_client()
    if not gemini_client.should_respond_to_message(user_message):
        logger.debug("@AI検出されず、AI応答処理をスキップ")
        return

    logger.info("@AI検出、AI応答生成を開始")
    try:
        # AI応答を生成（WebSocket用に高速化のためリトライ回数を3回に制限）
        generation_start = time.time()
        ai_response = await gemini_client.generate_response(user_message, max_retries=3)
        generation_time = time.time() - generation_start
        logger.info(f"AI応答生成完了: generation_time={generation_time:.2f}s, response_length={len(ai_response)}")

        # AI応答をメッセージとして保存・送信
        ai_message_data = {
            "id": f"ai_{channel_id}_{int(__import__('time').time() * 1000)}",
            "channel_id": channel_id,
            "user_id": "ai_haruto",
            "user_name": "ハルト",
            "content": ai_response,
            "timestamp": datetime.now(timezone(timedelta(hours=9))).isoformat(),
            "is_own_message": False,
        }

        # AI応答をデータベースに保存（共通のセッション管理ヘルパーを使用）
        ai_message_create = MessageCreate.model_validate(ai_message_data)

        # データベースに保存
        db_start = time.time()
        saved_ai_message = save_message_with_session_management(
            lambda session: crud.create_message(session, ai_message_create), db_session
        )
        db_time = time.time() - db_start
        logger.info(f"AI応答DB保存完了: db_time={db_time:.2f}s, message_id={saved_ai_message.id}")

        # AI応答を全クライアントにブロードキャスト
        broadcast_message = {
            "type": "message:broadcast",
            "data": {
                "id": saved_ai_message.id,
                "channel_id": saved_ai_message.channel_id,
                "user_id": saved_ai_message.user_id,
                "user_name": saved_ai_message.user_name,
                "content": saved_ai_message.content,
                "timestamp": saved_ai_message.timestamp.isoformat(),
                "is_own_message": False,
            },
        }

        broadcast_start = time.time()
        await manager.broadcast(json.dumps(broadcast_message))
        broadcast_time = time.time() - broadcast_start

        total_time = time.time() - start_time
        logger.info(
            f"AI応答送信完了: broadcast_time={broadcast_time:.2f}s, total_time={total_time:.2f}s, message_id={saved_ai_message.id}"
        )

    except Exception as e:
        error_time = time.time() - start_time
        logger.error(f"AI応答エラー: {str(e)}, error_time={error_time:.2f}s")

        # エラー時のフォールバック応答
        fallback_message_data = {
            "id": f"ai_error_{channel_id}_{int(__import__('time').time() * 1000)}",
            "channel_id": channel_id,
            "user_id": "ai_haruto",
            "user_name": "ハルト",
            "content": "通信に失敗しました😅 もう一度試してみてください！",
            "timestamp": datetime.now(timezone(timedelta(hours=9))).isoformat(),
            "is_own_message": False,
        }

        # エラーメッセージも全クライアントにブロードキャスト
        error_broadcast_message = {
            "type": "message:broadcast",
            "data": fallback_message_data,
        }

        await manager.broadcast(json.dumps(error_broadcast_message))
