from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# データベースファイルのパスを確実に設定
# 現在のファイルの場所を基準にして chat.db のパスを決定
DB_FILE_PATH = Path(__file__).parent / "chat.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE_PATH}"

# SQLiteの設定について：
# check_same_thread=Falseは開発・プロトタイプ段階での利便性のために設定
# 本番環境ではPostgreSQLやMySQLなどのマルチスレッド対応DBを推奨
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """データベースモデルのベースクラス"""

    pass


def get_db():
    """データベースセッションを取得"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
