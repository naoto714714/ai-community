"""リクエスト・レスポンススキーマ定義.

FastAPIのAPIエンドポイントで使用されるPydanticスキーマとデータクラスを定義します。
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, field_serializer


class UserType(str, Enum):
    """ユーザータイプ列挙型"""

    USER = "user"
    AI = "ai"


def to_camel(string: str) -> str:
    """snake_caseをcamelCaseに変換"""
    components = string.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])


def serialize_datetime_to_utc_iso(dt: datetime) -> str:
    """datetimeをUTC ISO形式の文字列に変換

    タイムゾーン情報のないdatetimeにはUTCタイムゾーンを割り当て、
    タイムゾーン情報のあるdatetimeはUTCに変換してからシリアライズする

    Args:
        dt: シリアライズするdatetimeオブジェクト

    Returns:
        UTCタイムゾーンでのISO形式文字列

    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    else:
        dt = dt.astimezone(UTC)
    return dt.isoformat()


class MessageBase(BaseModel):
    """メッセージの基本スキーマ.

    チャットメッセージの共通フィールドを定義し、他のメッセージスキーマのベースクラスとして使用されます。
    """

    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True, validate_by_alias=True)

    id: str
    channel_id: str
    user_id: str
    user_name: str
    user_type: UserType = UserType.USER
    content: str
    timestamp: datetime
    is_own_message: bool

    @field_serializer("timestamp")
    def serialize_timestamp(self, dt: datetime) -> str:
        """タイムスタンプをUTC ISO形式で出力"""
        return serialize_datetime_to_utc_iso(dt)


class MessageCreate(MessageBase):
    """メッセージ作成用スキーマ.

    新しいメッセージを作成する際に使用されるスキーマです。
    """

    pass


class MessageResponse(MessageBase):
    """メッセージレスポンス用スキーマ.

    APIレスポンスでメッセージ情報を返す際に使用されるスキーマです。
    """

    model_config = ConfigDict(
        from_attributes=True, alias_generator=to_camel, validate_by_name=True, validate_by_alias=True
    )

    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime) -> str:
        """created_atをUTC ISO形式で出力"""
        return serialize_datetime_to_utc_iso(dt)


class ChannelBase(BaseModel):
    """チャンネルの基本スキーマ.

    チャットチャンネルの共通フィールドを定義し、他のチャンネルスキーマのベースクラスとして使用されます。
    """

    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True, validate_by_alias=True)

    id: str
    name: str
    description: str | None = None


class ChannelResponse(ChannelBase):
    """チャンネルレスポンス用スキーマ.

    APIレスポンスでチャンネル情報を返す際に使用されるスキーマです。
    """

    model_config = ConfigDict(
        from_attributes=True, alias_generator=to_camel, validate_by_name=True, validate_by_alias=True
    )

    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime) -> str:
        """created_atをUTC ISO形式で出力"""
        return serialize_datetime_to_utc_iso(dt)


class MessagesListResponse(BaseModel):
    """メッセージ一覧レスポンス用スキーマ.

    メッセージ一覧APIのレスポンスで使用されるスキーマです。
    """

    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True, validate_by_alias=True)

    messages: list[MessageResponse]
    total: int
    has_more: bool


@dataclass
class MessageBroadcastData:
    """ブロードキャスト用メッセージデータ."""

    message_id: str
    channel_id: str
    user_id: str
    user_name: str
    user_type: str
    content: str
    timestamp: datetime
