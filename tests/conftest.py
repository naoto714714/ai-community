import asyncio
from collections.abc import AsyncGenerator

import pytest
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
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestingSessionLocal()

    Base.metadata.drop_all(bind=engine)
    app.dependency_overrides.clear()


@pytest.fixture
def client(test_db) -> TestClient:
    """同期テスト用クライアント"""
    return TestClient(app)


@pytest.fixture
async def async_client(test_db) -> AsyncGenerator[AsyncClient]:
    """非同期テスト用クライアント"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def seed_channels(test_db):
    """初期チャンネルデータの投入"""
    from src.backend.models import Channel

    channels = [
        Channel(id="1", name="雑談"),
        Channel(id="2", name="ゲーム"),
        Channel(id="3", name="音楽"),
        Channel(id="4", name="趣味"),
        Channel(id="5", name="ニュース"),
    ]

    test_db.add_all(channels)
    test_db.commit()

    return channels