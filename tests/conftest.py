import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.backend.database import Base, get_db

# テーブル重複定義エラーを回避するため、モデルは使用時にimportする
from src.backend.main import app

# テスト用データベース設定
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """セッション全体で使用するイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def test_db():
    """テスト用のインメモリデータベース"""
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        app.dependency_overrides.clear()


@pytest.fixture
def client(test_db) -> TestClient:
    """同期テスト用クライアント"""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(test_db) -> AsyncGenerator[AsyncClient]:
    """非同期テスト用クライアント"""
    from httpx import ASGITransport

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def seed_channels(test_db):
    """初期チャンネルデータの投入"""
    from src.backend.models import Channel

    channels = [
        Channel(id="1", name="雑談", description="何でも話せる場所"),
        Channel(id="2", name="ゲーム", description="ゲームについて語ろう"),
        Channel(id="3", name="音楽", description="音楽の話題はこちら"),
        Channel(id="4", name="趣味", description="趣味の共有"),
        Channel(id="5", name="ニュース", description="最新情報をシェア"),
    ]

    test_db.add_all(channels)
    test_db.commit()

    return channels
