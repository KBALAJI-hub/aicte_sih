from sqlmodel import SQLModel, Session, create_engine
# Import models so SQLModel metadata registers all tables
import app.models  # noqa: F401

# SQLite database configuration
sqlite_file_name = "apaar.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Engine with multi-threading enabled for FastAPI
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False}, echo=False)


def create_db_and_tables():
    """Create all registered tables in SQLite if they don't exist."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency yielding a database session per request."""
    with Session(engine) as session:
        yield session
