from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import SessionLocal, engine, get_db
from models import Base, Channel, Message
from schemas import ChannelResponse, MessagesListResponse

# 初期チャンネルデータ
INITIAL_CHANNELS = [
    {"id": "1", "name": "雑談"},
    {"id": "2", "name": "ゲーム"},
    {"id": "3", "name": "音楽"},
    {"id": "4", "name": "趣味"},
    {"id": "5", "name": "ニュース"},
]


def init_channels():
    """初期チャンネルをデータベースに作成"""
    db = SessionLocal()
    try:
        for channel_data in INITIAL_CHANNELS:
            existing = db.query(Channel).filter(Channel.id == channel_data["id"]).first()
            if not existing:
                channel = Channel(**channel_data)
                db.add(channel)
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 起動時処理
    Base.metadata.create_all(bind=engine)  # テーブル作成
    init_channels()  # 初期チャンネル作成
    yield
    # 終了時処理


app = FastAPI(
    title="AI Community Backend",
    description="Simple chat backend for AI Community",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "AI Community Backend API"}


@app.get("/api/channels", response_model=list[ChannelResponse])
async def get_channels(db: Session = Depends(get_db)):  # noqa: B008
    """チャンネル一覧取得"""
    channels = db.query(Channel).all()
    return channels


@app.get("/api/channels/{channel_id}/messages", response_model=MessagesListResponse)
async def get_channel_messages(
    channel_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),  # noqa: B008
):
    """指定チャンネルのメッセージ履歴取得"""
    # チャンネルの存在確認
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="Channel not found")

    # メッセージ取得
    messages = (
        db.query(Message)
        .filter(Message.channel_id == channel_id)
        .order_by(Message.created_at.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # 総数取得
    total = db.query(Message).filter(Message.channel_id == channel_id).count()
    has_more = (offset + limit) < total

    return MessagesListResponse(messages=messages, total=total, has_more=has_more)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
