import json
import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

try:
    # パッケージとして実行される場合（テスト等）
    from . import crud
    from .database import SessionLocal, get_db
    from .models import Channel
    from .schemas import ChannelResponse, MessageResponse, MessagesListResponse
    from .websocket import handle_websocket_message, manager
except ImportError:
    # 直接実行される場合
    import crud
    from database import SessionLocal, get_db
    from models import Channel
    from schemas import ChannelResponse, MessageResponse, MessagesListResponse
    from websocket import handle_websocket_message, manager

# 初期チャンネルデータ
INITIAL_CHANNELS = [
    {"id": "1", "name": "雑談", "description": "何でも話せる場所"},
    {"id": "2", "name": "ゲーム", "description": "ゲームについて語ろう"},
    {"id": "3", "name": "音楽", "description": "音楽の話題はこちら"},
    {"id": "4", "name": "趣味", "description": "趣味の共有"},
    {"id": "5", "name": "ニュース", "description": "最新情報をシェア"},
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
    # 注意: テーブル作成はAlembicマイグレーションで実行済み
    init_channels()  # 初期チャンネル作成
    yield
    # 終了時処理


app = FastAPI(
    title="AI Community Backend",
    description="Simple chat backend for AI Community",
    version="0.1.0",
    lifespan=lifespan,
)

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    return crud.get_channels(db)


# デフォルト値の定数定義
DEFAULT_MESSAGE_LIMIT = 100


@app.get("/api/channels/{channel_id}/messages", response_model=MessagesListResponse)
async def get_channel_messages(
    channel_id: str,
    limit: int = DEFAULT_MESSAGE_LIMIT,
    offset: int = 0,
    db: Session = Depends(get_db),  # noqa: B008
):
    """指定チャンネルのメッセージ履歴取得"""
    # チャンネルの存在確認
    channel = db.query(Channel).filter(Channel.id == channel_id).first()
    if not channel:
        raise HTTPException(status_code=404, detail="チャンネルが見つかりません")

    # メッセージ取得
    message_models = crud.get_channel_messages(db, channel_id, offset, limit)
    messages = [MessageResponse.model_validate(msg) for msg in message_models]

    # 総数取得
    total = crud.get_channel_messages_count(db, channel_id)
    has_more = (offset + limit) < total

    return MessagesListResponse(messages=messages, total=total, has_more=has_more)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                # データベースセッションを作成して渡す
                db = SessionLocal()
                try:
                    await handle_websocket_message(websocket, message, db_session=db)
                finally:
                    db.close()
            except json.JSONDecodeError:
                logger.error(f"無効なJSONを受信: {data}")
                # クライアントにエラー応答を送信
                error_response = {"type": "error", "data": {"success": False, "error": "無効なJSON形式"}}
                await websocket.send_text(json.dumps(error_response))
            except Exception as e:
                logger.error(f"WebSocketメッセージ処理エラー: {str(e)}")
                # 一般的なエラー応答を送信
                error_response = {"type": "error", "data": {"success": False, "error": "内部サーバーエラー"}}
                await websocket.send_text(json.dumps(error_response))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("WebSocket接続が閉じられました")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
