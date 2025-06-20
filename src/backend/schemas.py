from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, field_serializer


def to_camel(string: str) -> str:
    """Convert snake_case to camelCase"""
    components = string.split("_")
    return components[0] + "".join(word.capitalize() for word in components[1:])


class MessageBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True, validate_by_alias=True)

    id: str
    channel_id: str
    user_id: str
    user_name: str
    content: str
    timestamp: datetime
    is_own_message: bool

    @field_serializer("timestamp")
    def serialize_timestamp(self, dt: datetime) -> str:
        """タイムスタンプをUTC ISO形式で出力"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.isoformat()


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=to_camel, validate_by_name=True, validate_by_alias=True
    )

    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime) -> str:
        """created_atをUTC ISO形式で出力"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.isoformat()


class ChannelBase(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True, validate_by_alias=True)

    id: str
    name: str
    description: str | None = None


class ChannelResponse(ChannelBase):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=to_camel, validate_by_name=True, validate_by_alias=True
    )

    created_at: datetime

    @field_serializer("created_at")
    def serialize_created_at(self, dt: datetime) -> str:
        """created_atをUTC ISO形式で出力"""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt.isoformat()


class MessagesListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True, validate_by_alias=True)

    messages: list[MessageResponse]
    total: int
    has_more: bool
