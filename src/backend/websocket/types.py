"""WebSocket関連の型定義"""

from typing import TypedDict

from ..schemas import UserType


class WebSocketMessageData(TypedDict):
    """WebSocketメッセージのdata部分の型定義"""

    id: str
    channel_id: str
    user_id: str
    user_name: str
    user_type: UserType
    content: str
    timestamp: str
    is_own_message: bool


class WebSocketMessage(TypedDict):
    """WebSocketメッセージの型定義"""

    type: str
    data: WebSocketMessageData | None
