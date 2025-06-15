from datetime import datetime

from pydantic import BaseModel


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
    created_at: datetime

    class Config:
        from_attributes = True


class ChannelBase(BaseModel):
    id: str
    name: str


class ChannelResponse(ChannelBase):
    created_at: datetime

    class Config:
        from_attributes = True


class MessagesListResponse(BaseModel):
    messages: list[MessageResponse]
    total: int
    has_more: bool
