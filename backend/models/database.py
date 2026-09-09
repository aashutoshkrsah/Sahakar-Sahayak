import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Ensure data directory exists
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DEFAULT_DB_PATH = os.path.join(DATA_DIR, "sahakar_sahayak.db")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH}")

# SQLite requires check_same_thread=False for multithreaded FastAPI requests
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency that provides a SQLAlchemy database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables and perform lightweight schema migrations if necessary."""
    # Import all models to ensure they are registered with Base.metadata
    from backend.models.user import User  # noqa: F401

    Base.metadata.create_all(bind=engine)

    # Lightweight migration check for SQLite
    if DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            inspector = inspect(engine)
            if "users" in inspector.get_table_names():
                columns = [col["name"] for col in inspector.get_columns("users")]
                if "phone" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN phone VARCHAR(50)"))
                    conn.commit()
                if "user_type" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN user_type VARCHAR(50) DEFAULT 'Citizen'"))
                    conn.commit()
                if "preferred_language" not in columns:
                    conn.execute(text("ALTER TABLE users ADD COLUMN preferred_language VARCHAR(10) DEFAULT 'en'"))
                    conn.commit()
