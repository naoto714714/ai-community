from datetime import datetime

from pydantic import BaseModel, ConfigDict


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


class MessageCreate(MessageBase):
    pass


class MessageResponse(MessageBase):
    model_config = ConfigDict(
        from_attributes=True, alias_generator=to_camel, validate_by_name=True, validate_by_alias=True
    )

    created_at: datetime


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


class MessagesListResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, validate_by_name=True, validate_by_alias=True)

    messages: list[MessageResponse]
    total: int
    has_more: bool
