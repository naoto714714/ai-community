import logging
import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# ログ設定
logger = logging.getLogger(__name__)

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

    # 型安全性の確保
    if all([DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD]):
        try:
            # 環境変数の型チェック済みのため安全にstr変換
            encoded_user = quote_plus(str(DB_USER))
            encoded_password = quote_plus(str(DB_PASSWORD))
            SQLALCHEMY_DATABASE_URL = (
                f"postgresql://{encoded_user}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
            )
            logger.info("Supabase PostgreSQL接続設定を使用します")
        except Exception:
            logger.error("PostgreSQL接続情報の処理に失敗しました。SQLiteにフォールバックします")
            DB_FILE_PATH = Path(__file__).parent / "chat.db"
            SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_FILE_PATH.as_posix()}"
    else:
        logger.info("PostgreSQL環境変数が不完全です。SQLiteを使用します")
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
