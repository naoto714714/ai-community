import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# 環境変数を読み込み
load_dotenv()

# データベース接続設定
#
# 優先順位:
# 1. テスト環境: SQLiteインメモリDB（:memory:）- テスト専用、ファイル生成なし
# 2. 本番環境: Supabase PostgreSQL - 本番・ステージング環境
# 3. 開発環境: SQLite（ローカルファイル）- 開発・デバッグ用のフォールバック
#
# 使い分けガイド:
# - テスト実行時: TESTING=true で自動的にインメモリDBを使用
# - 本番・ステージング: DB_HOST等の環境変数を設定してSupabase使用
# - ローカル開発: 環境変数未設定時にchat.dbファイルを使用（.gitignoreで除外済み）

if os.getenv("TESTING") == "true":
    # テスト環境: SQLiteインメモリDB（ファイル生成を防ぐ）
    SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
else:
    # Supabase PostgreSQL接続設定の確認
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

    if all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
        # 本番環境: Supabase PostgreSQL
        # Supabase Direct Connection形式
        # postgresql://user:password@host:port/dbname?sslmode=require
        # ユーザー名とパスワードの両方をURLエンコード（特殊文字対応）
        # all()でバリデーション済みのため、型アサーションを使用
        encoded_user = quote_plus(DB_USER)  # type: ignore[arg-type]
        encoded_password = quote_plus(DB_PASSWORD)  # type: ignore[arg-type]
        SQLALCHEMY_DATABASE_URL = (
            f"postgresql://{encoded_user}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
        )
    else:
        # 開発環境: SQLiteローカルファイル（環境変数が設定されていない場合のフォールバック）
        # 注意: chat.dbファイルは.gitignoreで除外済み（セキュリティ・容量対策）
        DB_FILE_PATH = Path(__file__).parent / "chat.db"
        SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE_PATH.as_posix()}"

# PostgreSQL用の設定（connection pooling）
# SQLiteの場合は従来の設定を維持
if SQLALCHEMY_DATABASE_URL.startswith("postgresql://"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=3600,
    )
else:
    # SQLite用設定（テスト環境やフォールバック時）
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
