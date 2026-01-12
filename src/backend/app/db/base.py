from app.db.session import engine
from app.models.base import Base
from app.models.chat import ChatMessage  # noqa: F401 - Import to register with metadata
from app.models.task import Task  # noqa: F401 - Import to register with metadata
from app.models.user import User  # noqa: F401 - Import to register with metadata


def init_db() -> None:
    """
    Initialize database tables.
    This function creates all tables if they don't exist.
    It's safe to call multiple times - it will only create missing tables.
    """
    Base.metadata.create_all(bind=engine)
