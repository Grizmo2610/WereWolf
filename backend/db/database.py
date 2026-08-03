import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.settings import get_settings

settings = get_settings()
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = settings.db_path
if not os.path.isabs(db_path):
    db_path = os.path.join(PROJECT_ROOT, db_path)
os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db() -> None:
    from db.models import Base
    Base.metadata.create_all(bind=engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
