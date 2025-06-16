from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./chat.db"

# SQLiteの設定について：
# check_same_thread=Falseは開発・プロトタイプ段階での利便性のために設定
# 本番環境ではPostgreSQLやMySQLなどのマルチスレッド対応DBを推奨
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
