from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MessageBase(BaseModel):
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
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime


class ChannelBase(BaseModel):
    id: str
    name: str


class ChannelResponse(ChannelBase):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime


class MessagesListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int
    has_more: bool
