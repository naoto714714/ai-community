"""データベースセッション管理ユーティリティ"""

from collections.abc import Callable
from typing import Any

from sqlalchemy.orm import Session

# 型のエイリアス - Messageモデルまたは保存結果
MessageResult = Any


def save_message_with_session_management(
    message_create_func: Callable[[Session], Any],
    db_session: Session | None = None,
    auto_commit: bool = True,
) -> MessageResult:
    """セッション管理を共通化したメッセージ保存ヘルパー関数

    Args:
        message_create_func: セッションを受け取ってメッセージを作成する関数
        db_session: オプショナルセッション。テスト環境で使用される。
                    Noneの場合は新しいセッションを作成（本番環境）
        auto_commit: 外部セッション使用時にcommitを実行するかどうか。
                    テスト環境ではFalseにしてトランザクション境界を維持

    Returns:
        保存されたメッセージオブジェクト

    """
    try:
        # パッケージとして実行される場合
        from ..database import SessionLocal
    except ImportError:
        try:
            # 直接実行される場合
            from src.backend.database import SessionLocal
        except ImportError:
            # 最後の手段として
            from database import SessionLocal

    if db_session is not None:
        # 外部セッション使用時: トランザクション境界管理をauto_commitで制御
        try:
            result = message_create_func(db_session)
            if auto_commit:
                db_session.commit()
            return result
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
