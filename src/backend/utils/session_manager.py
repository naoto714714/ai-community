"""データベースセッション管理ユーティリティ"""

from collections.abc import Callable
from typing import Any

from sqlalchemy.orm import Session


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
        from ..database import SessionLocal
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
            result = message_create_func(db)
            db.commit()
            return result
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
