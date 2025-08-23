# python-training/lessons/points_system/src/core/db.py

from contextlib import contextmanager
from core.config import settings
from sqlmodel import Session, create_engine

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI), pool_pre_ping=True)

@contextmanager
def get_session():
    """
    Context manager for creating a DB session using SQLModel.
    Falls back to a dummy session if DB is unavailable.
    """
    if engine is None:
        print("⚠️  Dummy session: changes won't be persisted.")
        yield None
        return

    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"❌ Error during DB operation: {e}")
        raise
    finally:
        session.close()
